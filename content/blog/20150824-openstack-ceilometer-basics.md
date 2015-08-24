Title: OpenStack Ceilometer basics
Date: 2015-08-24
Tags: openstack, ceilometer
Slug: openstack-ceilometer-basics
Author: morten.hanshaugen@met.no
Status: draft

## Ceilometer - OpenStack Telemetry

| OpenStack uses Ceilometer to measure Cloud usage.  <p />Telemetry is nice, as infrastructure utilization gets visible to users, developers, project leaders, management and to the IT department for utilization and budgetary purposes. | ![The Ceilometer]({filename}/images/Single_Lens_Ceilometer.JPG) |

### Telemetry for OpenStack
Getting telemetry from OpenStack quickly changed from optimism to frustration. 
OpenStack has all of these really nice APIs you can use to query all kinds of information, but there is no mature project for setting it in a system - and we really did not want to start writing a Cloud accounting system from scratch.

#### Simple start - the API
How to do it could be better documented. This is basics:

Get a token:
```. openrc    # openrc sets a number of useful variables
echo $OS_AUTH_URL
http://localhost:5000/v2.0
```

Store the adminURL in the ADMIN_URL variable (this is a quick and dirty method):
```ADMIN_URL=`curl -s -X POST $OS_AUTH_URL/tokens -H "Content-Type: application/json" -d '{"auth": {"tenantName": "'"$OS_TENANT_NAME"'", "passwordCredentials": {"username": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"}}}' | python -c 'import sys, json; print json.load(sys.stdin)["access"]["serviceCatalog"][3]["endpoints"][0]["adminURL"]'`v$OS_VOLUME_API_VERSION/
echo $ADMIN_URL
http://localhost:8777/v2/

TOKEN=`curl -s -X POST $OS_AUTH_URL/tokens -H "Content-Type: application/json" -d '{"auth": {"tenantName": "'"$OS_TENANT_NAME"'", "passwordCredentials": {"username": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"}}}' | python -c 'import sys, json; print json.load(sys.stdin)["access"]["token"]["id"]'`

echo $TOKEN
3df105345ada4460b16ee11c06617cf7
```

Please note that the tests below will not output anything useful if you have a newly installed OpenStack/Devstack with no data or instances in the database.

Quick test listing of meters:
```$ curl -H X-Auth-Token:$TOKEN "${ADMIN_URL}meters" | python -m json.tool|grep name|head -3
    	"name": "network.incoming.packets",
    	"name": "network.outgoing.bytes",
    	"name": "network.outgoing.packets",
```

Query list of instances: 
```curl -H X-Auth-Token:$TOKEN "${ADMIN_URL}meters/instance?q.field=metadata.event_type&q.value=compute.instance.exists" | python -m json.tool | head
[
	{
    	"counter_name": "instance",
    	"counter_type": "gauge",
    	"counter_unit": "instance",
    	"counter_volume": 1.0,
    	"message_id": "132e401a-26e2-11e5-8ca8-fef0e2547b3a",
    	"project_id": "08b96944c51e45cc847b2a1901ec58c0",
    	"recorded_at": "2015-07-10T09:00:13.117000",
    	"resource_id": "ca3a8684-f406-464d-8ae4-10982613db0e",
```

Query list of instances where timestamp is newer than a date: 
```curl -X GET -H X-Auth-Token:$TOKEN -H "Content-Type: application/json" -d '{"q": [{"field": "timestamp", "op": "ge", "value": "2014-04-01T13:34:17"}]}' ${ADMIN_URL}meters/instance | python -m json.tool
<the same as above>
```

A last example to help you along:
```curl -X GET -H X-Auth-Token:$TOKEN -H "Content-Type: application/json" -d '{"q": [{"field": "timestamp", "op": "ge", "value": "2014-04-01T13:34:17"}, {"field": "resource_id", "op": "eq", "value": "82a1371d-a1a3-4f98-9781-8663b262ee7e"}]}' ${ADMIN_URL}meters/instance
```

See this link for examples of how to use the API:
http://docs.openstack.org/developer/ceilometer/webapi/v2.html#api-queries

#### Command line clients
See OpenStack command-line clients for detail on how to install command line clients and getting credentials:
http://docs.openstack.org/api/quick-start/content/index.html#getting-credentials-a00665
```nova image-list
nova flavor-list
etc
```

In need of a Ceilometer project to contribute to
We master the basics. How to find an OpenStack Ceilometer project to adapt and contribute to?

