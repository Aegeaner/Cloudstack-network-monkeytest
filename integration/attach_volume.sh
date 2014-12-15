#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

usage() {
  printf "Usage: %s:  -z <zoneid>  -d <diskofferingid>  \n" $(basename $0) >&2
}

zflag=
dflag=

while getopts 'z:d:' OPTION
do
   case $OPTION in
    z)  zflag=1
            zoneid="$OPTARG"
            ;;
        d)  dflag=1
            diskofferingid="$OPTARG"
            ;;
	?)  usage
            exit
            ;;
    esac
done

if [ "$zflag$dflag" != "11" ]
then
    usage
    exit
fi

vmids=`CM_CUSTOM list virtualmachines networkid=$networkid filter=id | grep id | awk '{ gsub(/"/,"",$NF);print $NF }' `
CM_CUSTOM set asyncblock false

i=1
vmids=`CM_CUSTOM list virtualmachines networkid=$networkid filter=id | grep id | awk '{ gsub(/"/,"",$NF);print $NF }' `
for vmid in $vmids
do
    i=$((i+1))
    jobid=`CM_CUSTOM create volume zoneid=$zoneid name=Data-$i diskofferingid=$diskofferingid | grep jobid | awk '{ gsub(/"/,"",$NF);print $NF }'`
    volumeid=`CM_CUSTOM query asyncjobresult jobid=$jobid | grep \"id\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }' `
    echo "Attach volume with id $volumeid to virtual machine with id: $vmid"
    CM_CUSTOM attach volume id=$volumeid virtualmachineid=$vmid 1>/dev/null
done

