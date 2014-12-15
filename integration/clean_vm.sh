#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

usage() {
  printf "Usage: %s:  -z <zoneid>  -n <networkid>  \n" $(basename $0) >&2
}

zflag=
nflag=

while getopts 'z:n:' OPTION
do
   case $OPTION in
    z)  zflag=1
            zoneid="$OPTARG"
            ;;
	n)  nflag=1
            networkid="$OPTARG"
            ;;
	?)  usage
            exit
            ;;
    esac
done

if [ "$zflag$nflag" != "11" ]
then
    usage
    exit
fi

CM_CUSTOM set asyncblock false

vmids=`CM_CUSTOM list virtualmachines networkid=$networkid filter=id | grep id | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }' `
for vmid in $vmids
do
    echo "Destroying virtual machine with id: $vmid"
    CM_CUSTOM destroy virtualmachine id=$vmid expunge=true 1>/dev/null
done

