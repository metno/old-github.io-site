Title: Production OpenStack
Date: 2015-12-15
Tags: private cloud, OpenStack
Slug: OpenStack
Authors: sverre.stoltenberg@met.no

[consul]: https://consul.io/
[registrator]: https://github.com/gliderlabs/registrator
[docker-machine]: https://docs.docker.com/machine/
[docker]: https://docker.io/
[swarm]: https://github.com/docker/swarm
[docker-compose]: https://docs.docker.com/compose/
[ansible]: http://www.ansible.com/
[whatsmyip]: https://github.com/pklaus/docker-deployments/tree/master/whatsmyip
[percona-XtraDB]: https://www.percona.com/software/mysql-database/percona-xtradb-cluster
[rabbitmq]: https://www.rabbitmq.com/
[haproxy]: http://www.haproxy.org/
[moxi]: https://code.google.com/p/moxi/
[keepalived]: http://www.keepalived.org/
[ceph]: http://ceph.com/
[sensu]: https://sensuapp.org/
[grafana]: http://grafana.org/
[centos]: http://www.centos.org/
[nova]: http://www.openstack.org/software/releases/liberty/components/nova
[telegraf]: https://github.com/influxdb/telegraf
[influxdb]: https://influxdata.com/
[docker overlay network]: https://docs.docker.com/engine/userguide/networking/get-started-overlay/
[memcached]: http://memcached.org/

## Requirements

The requirement of this OpenStack setup is to have a highly available
cloud spread over two or more data centers. It will replace the current
solution where a user is requesting a VM from the infrastructure
group, which is ineffective and time consuming.

The aim of the setup is to be able to lose one data center, without
affecting production. The use of containers makes it easier to scale
the services by adding more servers, and to set up an identical
staging environment to test upgrades or develop new services. 

It was also a good opportunity to introduce new technology and when
you setup an OpenStack service as a container from scratch, you get
pretty familiar with the service.

We are not using [docker overlay network] at the moment, but it would
be nice to have it in the future, so we don't have to expose too many
internal services.

### Basic building blocks

* [centos] The OS used of most containers and on the physical hosts
* [consul] Service discovery
* [registrator] Feeds consul with info about containers
* [docker-machine] Install [docker] and [swarm]
* [docker] The container manager 
* [swarm] Manage containers on many hosts
* [docker-compose] Start and stop containers
* [ansible] Configuration management

### Cluster services

* [consul] Service discovery
* [swarm] Unifying docker on different physical hosts
* [percona-XtraDB] Clustered mysql database
* [rabbitmq] Messagequeue
* [haproxy] Loadbalancing api between datacenters, and terminate SSL
* [moxi] Clustered [memcached]
* [keepalived] Handeling shared ip address between datacenters.

### Other services used

* [ceph] Block storage
* [sensu] Service monitoring
* [influxdb] time series database
* [grafana] Graphing from [influxdb]
* [telegraf] Feeding [influxdb]
* [whatsmyip] Used by containers to discover what ip address the host they run on has.


## Example: nova container

### Docker file

Here we make a container image, that can run all openstack nova
services, depending on how it is started. It get password and special
configuration from an environment file.

```Dockerfile
FROM centos

RUN yum install -y http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm \
    yum install -y epel-release \
    yum install -y http://buildlogs.centos.org/centos/7/cloud/openstack-liberty/centos-release-openstack-liberty-1-3.el7.noarch.rpm
  
RUN yum install -y \
    bind-utils \
    crudini \
    mysql-client \
    openstack-nova-api \
    openstack-nova-api \
    openstack-nova-cert \
    openstack-nova-common \
    openstack-nova-conductor \
    openstack-nova-console \
    openstack-nova-novncproxy \
    openstack-nova-scheduler \
    python-openstackclient \
    python-pip

ADD entrypoint.sh /entrypoint.sh
  
ENTRYPOINT ["/entrypoint.sh"]
  
CMD ["/bin/bash"]
```

### entrypoint.sh

```bash
#!/bin/bash 
  
# need to disable iptables-save and restore, at least for nova-api
rm -f /usr/sbin/iptables-save
ln -s /bin/true /usr/sbin/iptables-save
rm -f /usr/sbin/iptables-restore
ln -s /bin/true /usr/sbin/iptables-restore
  
# Set verbose and job control
set -v -m 
  
rm /etc/nova/nova.conf
touch /etc/nova/nova.conf
chown root.nova /etc/nova/nova.conf
chown 640 /etc/nova/nova.conf
  
CONF="crudini --set /etc/nova/nova.conf"
 
$CONF database connection mysql://$NOVA_DBUSER:$NOVA_DBPASS@$MYSQL_HOST/nova?charset=utf8
  
$CONF DEFAULT verbose true
$CONF DEFAULT debug true
$CONF DEFAULT logfile ""
$CONF DEFAULT auth_strategy keystone
  
#availability zones
$CONF DEFAULT default_availability_zone $DATACENTER
$CONF DEFAULT default_schedule_zone $DATACENTER
$CONF DEFAULT cross_az_attach False
  
# rabbit
$CONF DEFAULT rpc_backend rabbit
$CONF DEFAULT rabbit_host $RABBIT_HOST
$CONF DEFAULT rabbit_userid $RABBIT_USER
$CONF DEFAULT rabbit_password $RABBIT_PASS
  
# Legacy networking http://docs.openstack.org/icehouse/install-guide/install/yum/content/section_nova-networking.html
$CONF DEFAULT network_api_class nova.network.api.API
$CONF DEFAULT security_group_api nova
  
$CONF DEFAULT network_manager nova.network.manager.VlanManager
$CONF DEFAULT vlan_start 400
$CONF DEFAULT vlan_interface br0
  
$CONF glance host $ENDPOINT_IP
$CONF oslo_concurrency lock_path /var/lib/nova/tmp
  
# Check if the novadatabase exist, if not create
if ! mysql -h$MYSQL_HOST -u$MYSQL_DBUSER -p$MYSQL_DBPASS nova -e 'QUIT' ; then
    mysql -h$MYSQL_HOST -u$MYSQL_DBUSER -p$MYSQL_DBPASS mysql -e "CREATE DATABASE nova;"
    mysql -h$MYSQL_HOST -u$MYSQL_DBUSER -p$MYSQL_DBPASS mysql -e "GRANT ALL ON nova.* TO '$NOVA_DBUSER'@'%' IDENTIFIED BY '$NOVA_DBPASS';"
fi
  
nova-manage db sync
  
OS="openstack --os-token=$ADMIN_TOKEN --os-url=$KEYSTONE_ADMIN_ENDPOINT/$KEYSTONE_ENDPOINT_VERSION"
   
# Create a nova service
if ! $OS service show nova ; then
    $OS service create --name nova --description "OpenStack Compute" compute
fi
  
# Create nova endpoints
if ! $OS endpoint show compute ; then
    $OS endpoint create --region $ENDPOINT_REGION --publicurl $NOVA_ENDPOINT --internalurl $NOVA_ENDPOINT --adminurl $NOVA_ENDPOINT compute
fi

# Create service project
if ! $OS project show service ; then
    $OS project create --description "Service Project" service
fi

# Create service role
if ! $OS role show service ; then
    $OS role create service
fi

# give nova admin role in service project
if ! $OS user role list | grep "service.*nova" ; then
    # Add the admin role to the admin project and user
    $OS role add --project service --user nova admin
fi

exec $@
```

### docker-compose.yml

```yaml
nova-api:
  image: 157.249.186.12:50000/nova
  hostname: nova-api
  restart: always
  env_file:
    - openstack.env
    - openstack-endpoints.env
  ports:
    - "58773:8773"
    - "58774:8774"
    - "58775:8775"
  expose:
    - "8773"
    - "8774"
    - "8775"
  environment: 
    - "constraint:node==/ares-[ab][0-9]/"
    - SERVICE_NAME=nova-api
  dns:
    - "172.17.0.1"
    - "157.249.16.22"
    - "157.249.16.20"
  command: su -s /bin/bash -c /usr/bin/nova-api nova
```

