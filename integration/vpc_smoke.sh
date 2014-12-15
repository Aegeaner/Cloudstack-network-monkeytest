#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

zoneid='6ba1c648-b924-4879-88a8-1c31c0bf9c43'
vpcofferingid='817416e3-428d-4517-a44c-ab1d3d533173'
networkofferingid='def11490-217d-4e1b-98ca-9d0eaae76561'
nolb_networkofferingid='a59c2326-c19e-4d84-be3a-2266e8ec2294'

CM_CUSTOM set asyncblock true

vpcname='VPC-Smoke-Test'
vpcid=`CM_CUSTOM create vpc name=$vpcname displaytext=$vpcname cidr=10.6.0.0/16 vpcofferingid=$vpcofferingid zoneid=$zoneid \
| grep \"id\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
echo "VPC with id $vpcid created."

t1id=`CM_CUSTOM create network name=${vpcname}-tier1 displaytext=${vpcname}-tier1 networkofferingid=$networkofferingid zoneid=$zoneid vpcid=$vpcid netmask=255.255.255.0 gateway=10.6.1.1 \
| grep \"id\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
echo "VPC tier 1 with network id $t1id created."

t2id=`CM_CUSTOM create network name=${vpcname}-tier1 displaytext=${vpcname}-tier2 networkofferingid=$nolb_networkofferingid zoneid=$zoneid vpcid=$vpcid netmask=255.255.255.0 gateway=10.6.2.1 \
| grep \"id\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
echo "VPC tier 2 with network id $t2id created."

t3id=`CM_CUSTOM create network name=${vpcname}-tier1 displaytext=${vpcname}-tier3 networkofferingid=$nolb_networkofferingid zoneid=$zoneid vpcid=$vpcid netmask=255.255.255.0 gateway=10.6.3.1 \
| grep \"id\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
echo "VPC tier 3 with network id $t3id created."

CM_CUSTOM delete network id=$t1id 1>/dev/null
echo "VPC tier 1 with network id $t1id destroyed."
CM_CUSTOM delete network id=$t2id 1>/dev/null
echo "VPC tier 2 with network id $t2id destroyed."
CM_CUSTOM delete network id=$t3id 1>/dev/null
echo "VPC tier 3 with network id $t3id destroyed."

CM_CUSTOM delete vpc id=$vpcid 1>/dev/null
echo "VPC with id $vpcid destroyed."


