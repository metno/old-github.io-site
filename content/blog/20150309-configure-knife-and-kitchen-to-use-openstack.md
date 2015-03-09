Title: How to Configure Knife and Test Kitchen to use OpenStack
Date: 2015-03-09
Tags: knife, kitchen, openstack, chef, nova, neutron, glance, tools, howto
Slug: configure-knife-and-test-kitchen-to-use-openstack
Author: arne.sund@met.no

[Cloud-init]: http://cloudinit.readthedocs.org/en/latest/

_Originally published on [arnesund.com](http://arnesund.com/2015/03/01/how-to-configure-knife-and-test-kitchen-to-use-openstack/)_

When developing Chef cookbooks, Knife and Test Kitchen (hereafter just "Kitchen") are essential tools in the workflow. Both tools can be set up to use OpenStack to make it easy to create VMs for testing regardless of the capabilities of the workstation used. It's great for testing some new recipe in a cookbook or making sure changes do not break existing cookbook functionality. This post will go through the configuration of both tools to ensure they use OpenStack instead of the default Vagrant drivers.

## Install software and dependencies

First, it is necessary to install the software, plugins and dependencies. Let's start with some basic packages:

```bash
sudo apt-get install ruby1.9 git
sudo apt-get install make autoconf gcc g++ zlib1g-dev bundler
```

### Chef Development Kit

The [Chef Development Kit](https://docs.chef.io/#chef-dk-title) is a collection of very useful tools for any cookbook developer. It includes tools like Knife, Kitchen, Berkshelf, Foodcritic, and more. Fetch download links for the current release from the [Chef-DK download page](https://downloads.chef.io/chef-dk/) and install it, for example like this for Ubuntu:

```bash
wget https://opscode-omnibus-packages.s3.amazonaws.com/ubuntu/12.04/x86_64/chefdk_0.4.0-1_amd64.deb
sudo dpkg -i chefdk_0.4.0-1_amd64.deb
```

### Kitchen OpenStack driver

By default, Kitchen uses Vagrant as the driver to create virtual machines for running tests. To get OpenStack support, install the [Kitchen OpenStack driver](https://github.com/test-kitchen/kitchen-openstack). The recommended way of installing it is to add the Ruby gem to the Gemfile in your cookbook and use Bundler to install it:

```bash
echo 'gem "kitchen-openstack"' >> Gemfile
sudo bundle
```

### Knife OpenStack plugin

With the [OpenStack plugin](https://github.com/chef/knife-openstack) Knife is able to create new OpenStack VMs and bootstrap them as nodes on your Chef server. It can also list VMs and delete VMs. Install the plugin with:

```bash
gem install knife-openstack
```

### OpenStack command line clients

The command line clients for OpenStack are very useful for checking values like image IDs, Neutron networks and so on. In addition, they offer one-line access to actions like creating new VMs, allocating new floating IPs and more. Install the clients with:

```bash
sudo apt-get install python-novaclient python-neutronclient python-glanceclient
```

## Configure Knife to use OpenStack

After installing the plugin to get OpenStack support for Knife, you need to append some lines to the Knife config file `~/.chef/knife.rb`:

```bash
cat >> ~/.chef/knife.rb <<EOF
# Knife OpenStack plugin setup
knife[:openstack_auth_url] = "#{ENV['OS_AUTH_URL']}/tokens"
knife[:openstack_username] = "#{ENV['OS_USERNAME']}"
knife[:openstack_password] = "#{ENV['OS_PASSWORD']}"
knife[:openstack_tenant] = "#{ENV['OS_TENANT_NAME']}"
EOF
```

What these lines do is to instruct Knife to use the contents of environment variables to authenticate with OpenStack when needed. The environment variables are the ones you get when you source the OpenStack RC file of your project. The RC file can be downloaded from the OpenStack web UI (Horizon) by navigating to Access & Security -> API Access -> Download OpenStack RC file. Sourcing the file makes sure the environment variables are part of the current shell environment, and is done like this (for an RC file called `openstack-rc.sh`):

```bash
$ . openstack-rc.sh
```

With this config in place Knife now has the power to create new OpenStack VMs in your project, list all active VMs and destroy VMs. In addition, it can be used to list available images, flavors and networks in OpenStack. I do however prefer to use the native OpenStack clients (glance, nova, neutron) for that, since they can perform lots of other valuable tasks like creating new networks and so on.

Below is an example of VM creation with Knife, using some of the required and optional arguments to the command. Issue `knife openstack server create --help` to get all available arguments. As a quick summary, the arguments I give Knife are the requested hostname of the server, the flavor (3 = m1.medium in my cluster), image ID of a CentOS 7 image, network ID, SSH key name and the default user account used by the image ("centos").

With the `--openstack-floating-ip` argument I tell Knife to allocate a floating IP to the new server. I could have specified a specific floating IP after that argument, which would have been allocated to the new server whether it was in use before or not. The only requirement is that it must be allocated to my OpenStack project before I try to use it.

```bash
$ knife openstack server create -N test-server -f 3 -I b206baa3-3a80-41cf-9850-49021b8bb3c1 --network-ids df7cc182-8794-4134-b700-1fb8f1fbf070 --openstack-ssh-key-id arnes --ssh-user centos --openstack-floating-ip --no-host-key-verify

Waiting for server [wait time = 600].........................
Instance ID 13493d82-8dc2-4b1d-87e8-3eeefa8defe2
Name test-server
Flavor 3
Image b206baa3-3a80-41cf-9850-49021b8bb3c1
Keypair arnes
State ACTIVE
Availability Zone nova
Floating IP Address: 10.0.1.242
Bootstrapping the server by using bootstrap_protocol: ssh and image_os_type: linux

Waiting for sshd to host (10.0.1.242)....done
Connecting to 10.0.1.242
10.0.1.242 Installing Chef Client...
10.0.1.242 Downloading Chef 11 for el...
10.0.1.242 Installing Chef 11
10.0.1.242 Thank you for installing Chef!
10.0.1.242 Starting first Chef Client run...
...
10.0.1.242 Running handlers complete
10.0.1.242 Chef Client finished, 0/0 resources updated in 1.328282722 seconds
Instance ID 13493d82-8dc2-4b1d-87e8-3eeefa8defe2
Name test-server
Public IP 10.0.1.242
Flavor 3
Image b206baa3-3a80-41cf-9850-49021b8bb3c1
Keypair arnes
State ACTIVE
Availability Zone nova
```

As an added benefit of creating VMs this way, they are automatically bootstrapped as Chef nodes with your Chef server!

## Configure Kitchen to use OpenStack

Kitchen has a config file `~/.kitchen/config.yml` where all the config required to use OpenStack should be placed. The config file is "global", meaning it's not part of any cookbook or Chef repository. The advantage of using the global config file is that the Kitchen config in each cookbook is reduced to just one line, which is good since that Kitchen config is commonly committed to the cookbook repository and shared with other developers. Other developers may not have access to the same OpenStack environment as you, so their Kitchen OpenStack config will differ from yours.

Run the following commands to initialize the necessary config for Kitchen:

```bash
mkdir ~/.kitchen
cat >> ~/.kitchen/config.yml <<EOF
---
driver:
 name: openstack
 openstack_username: <%= ENV['OS_USERNAME'] %>
 openstack_api_key: <%= ENV['OS_PASSWORD'] %>
 openstack_auth_url: <%= "#{ENV['OS_AUTH_URL']}/tokens" %>
 openstack_tenant: <%= ENV['OS_TENANT_NAME'] %>
 require_chef_omnibus: true
 image_ref: CentOS 7 GC 2014-09-16
 username: centos
 flavor_ref: m1.medium
 key_name: <%= ENV['OS_USERNAME'] %>
 floating_ip_pool: public
 network_ref:
 - net1
 no_ssh_tcp_check: true
 no_ssh_tcp_check_sleep: 30
EOF
```

There is quite a bit of config going on here, so I'll go through some of the most important parts. Many of the configuration options rely on environment variables which are set when you source the OpenStack RC file, just like for Knife. In addition, the following options may need to be customized according to your OpenStack environment:

 * image_ref: The name of a valid image to use when creating VMs
 * username: The username used by the chosen image, in this case "centos"
 * flavor_ref: A valid name of a flavor to use when creating VMs
 * key_name: Must match the name of your SSH key in OpenStack, here it is set to equal your username
 * floating_ip_pool: The name of a valid pool of public IP addresses
 * network_ref: A list of existing networks to connect new VMs to

To determine the correct values for image, flavor and network above, use the command line OpenStack clients. The Glance client can output a list of valid images to choose from:

```bash
$ glance image-list
+--------------------------------------+------------------------+-----+------+------------+--------+
| ID                                   | Name     | Disk Format | Container Format | Size | Status |
+--------------------------------------+------------------------+-----+------+------------+--------+
| ee2cc71b-3e2e-4b11-b327-f9cbf73a5694 | CentOS 6 GC 14-11-12   | raw | bare | 8589934592 | active |
| b206baa3-3a80-41cf-9850-49021b8bb3c1 | CentOS 7 GC 2014-09-16 | raw | bare | 8589934592 | active |
...
```

Set the image_ref in the Kitchen config to either the ID, the name or a regex matching the name.

Correspondingly, find the allowed flavors with the Nova client:

```bash
$ nova flavor-list
+----+-----------+-----------+------+-----------+------+-------+-------------+-----------+
| ID | Name      | Memory_MB | Disk | Ephemeral | Swap | VCPUs | RXTX_Factor | Is_Public |
+----+-----------+-----------+------+-----------+------+-------+-------------+-----------+
|  2 | m1.small  |    2048   |  20  |     0     |      |   1   |     1.0     |    True   |
|  3 | m1.medium |    4096   |  40  |     0     |      |   2   |     1.0     |    True   |
...
```

The network names are available using the neutron client. However, if you haven't created any networks yet, you can create a network, subnet and router like this:

```bash
neutron net-create net1
neutron subnet-create --name subnet1 net1 10.0.0.0/24
neutron router-create gw
neutron router-gateway-set gw public
neutron router-interface-add gw subnet1
```

These commands assume that the external network in your OpenStack cluster is named "public". Assuming the commands complete successfully you may use the network name "net1" in the Kitchen config file. To get the list of available networks, use the Neutron client with the net-list subcommand:

```bash
$ neutron net-list
+--------------------------------------+--------+----------------------------------------------------+
| id                                   | name   | subnets |
+--------------------------------------+--------+----------------------------------------------------+
| 2d2b2336-d7b6-4adc-b7f2-c92f98d4ec58 | public | 5ac43f4f-476f-4513-8f6b-67a758aa56e7 |
| e9dcbda9-cded-4823-a9fe-b03aadf33346 | net1   | 8ba65517-9bf5-46cc-a392-03a0708cd7f3 10.0.0.0/24 |
+--------------------------------------+--------+----------------------------------------------------+
```

With all that configured, Kitchen is ready to use OpenStack as the driver instead of Vagrant. All you need to do in a cookbook to make Kitchen use the OpenStack driver, is to change the "driver" statement in the ".kitchen.yml" config file in the cookbook root directory from "vagrant" to "openstack":

```bash
---
driver:
 name: openstack
```

So, lets take it for a spin:

```bash
$ kitchen create
-----> Starting Kitchen (v1.2.1)
-----> Creating <default-ubuntu-1404>...
 OpenStack instance <c08688f6-a754-4f43-a365-898a38fc06f8> created.
.........................
(server ready)
 Attaching floating IP from <public> pool
 Attaching floating IP <10.0.1.243>
 Waiting for 10.0.1.243:22...
 Waiting for 10.0.1.243:22...
 Waiting for 10.0.1.243:22...
 (ssh ready)
 Using OpenStack keypair <arnes>
 Using public SSH key <~/.ssh/id_rsa.pub>
 Using private SSH key <~/.ssh/id_rsa>
 Adding OpenStack hint for ohai
net.ssh.transport.server_version[3fe8926c1320]
net.ssh.transport.algorithms[3fe8926c06b4]
net.ssh.connection.session[3fe89270b420]
net.ssh.connection.channel[3fe89270b2cc]
Finished creating <default-ubuntu-1404> (0m50.68s).
-----> Kitchen is finished. (0m52.22s)
```

Voil&agrave; :)
