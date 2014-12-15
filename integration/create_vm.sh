#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

usage() {
  printf "Usage: %s:  -z <zoneid>  -n <networkid> -t <templateid> -s <serviceofferingid> -p <number>  \n" $(basename $0) >&2
}

zflag=
nflag=
tflag=
sflag=
pflag=

while getopts 'z:n:t:s:p:' OPTION
do
   case $OPTION in
    z)  zflag=1
            zoneid="$OPTARG"
            ;;
	n)  nflag=1
            networkid="$OPTARG"
            ;;
	t)  tflag=1
            templateid="$OPTARG"
            ;;
	s)  sflag=1
            serviceofferingid="$OPTARG"
            ;;
    p)  pflag=1
            num="$OPTARG"
            ;;
	?)  usage
            exit
            ;;
    esac
done

if [ "$zflag$nflag$tflag$sflag" != "1111" ]
then
    usage
    exit
fi

if [ "$pflag" != "1" ]
then
    num=1
fi

networkname=`CM_CUSTOM list networks id=$networkid filter=name | grep name | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
vmcount=`CM_CUSTOM list virtualmachines networkid=$networkid filter=count | grep count | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`

echo "Network name: $networkname"

CM_CUSTOM set asyncblock false

for i in $(seq 1 $num)
do
     vmname=$networkname-vm-$((vmcount+i))
     echo "Creating VM, Name: $vmname"
     jobid[$i]=`CM_CUSTOM deploy virtualmachine zoneid=$zoneid networkids=$networkid templateid=$templateid serviceofferingid=$serviceofferingid name=$vmname | grep id | tail -n 1 | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
done

touch passwords.txt
truncate -s 0 passwords.txt
finished=0

while [ $finished -eq 0 ]
do
  finished=1
  for i in $(seq 1 $num)
  do
     echo "Getting passwords for VM $i..."
     jid=${jobid[$i]}
     password=`CM_CUSTOM query asyncjobresult jobid=$jid | grep \"password\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
     vmname=`CM_CUSTOM query asyncjobresult jobid=$jid | grep \"name\" | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
     if [ -n "$password" ]
     then
       echo "Got password: $password"
       echo -e "$vmname\t$password" >> passwords.txt
     else
       finished=0
     fi
  done
  sleep 5
done

sort passwords.txt | uniq > passwords
rm -f passwords.txt
