Title: Google Web App using Spreadsheet
Date: 2015-12-14
Tags: network, sdn, clos, open, switch, 10Gbits, 40Gbits
Slug: open-clos-data-center-network
Authors: erlend.rosok@met.no, morten.hanshaugen@met.no

## Open Clos Data Center Network 

In 2015, MET Norway needed to replace an old core switch based network. Instead of replacing it, we defined the network as legacy infrastructure, and we invested in an open Clos leaf/spine network to be ready for SDN in connection to the OpenStack based production MET Cloud.

MET Norway purchased 14 Juniper QFX5100-24Q 40Gbit switches with aggregate backbone capacity of 1.2Tbits. The new data center network is pure layer 3, L2 does not extend outside each leaf switch.

### EBGP
EBGP is used between all leafs and spines. EBGP is also used between the border leafs and GWs. BGP peers are configured to only accept specific routes, they will also only send specified routes.

### OSPF
We're using OSPF between leafs and zone switches (see illustration). This is redistributed into bgp in order to connected the openstack network with the rest of the cloud.

### LLDP
LLDP is enabled on all physical ports in order to exchange neighbor information between servers and switches. This is used to map cloud servers physical location.

### VXLAN
vxlan is used to tunnel layer 2 subnet over the layer 3 links.

![MET Data Center Network]({filename}/images/Data-Center-Network.png)

