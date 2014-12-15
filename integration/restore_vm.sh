#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

usage() {
  printf "Usage: %s:  -z <zoneid>  -n <networkid> -t <templateid>  \n" $(basename $0) >&2
}

zflag=
nflag=

while getopts 'z:n:t:' OPTION
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
	?)  usage
            exit
            ;;
    esac
done

if [ "$zflag$nflag$tflag" != "111" ]
then
    usage
    exit
fi

vmids=`CM_CUSTOM list virtualmachines networkid=$networkid filter=id | grep id | awk '{ gsub(/"/,"",$NF);print $NF }' `
CM_CUSTOM set asyncblock false

vmids=`CM_CUSTOM list virtualmachines networkid=$networkid filter=id | grep id | awk '{ gsub(/"/,"",$NF);print $NF }' `

i=1
for vmid in $vmids
do
    echo "Restoring virtual machine with vm id: $vmid, and template id: $templateid"
    jobid[$i]=`CM_CUSTOM restore virtualmachine virtualmachineid=$vmid templateid=$templateid | grep id | tail -n 1 | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
    i=$((i+1))
done

echo "................................................................................................."

finished=0
failed=0
num=$((i-1))

while [ $finished -eq 0 ] && [ $failed -eq 0 ]
do
  finished=1
  for i in $(seq 1 $num)
  do
    jid=${jobid[$i]}
    response=`CM_CUSTOM query asyncjobresult jobid=$jid`
    jobstatus=`echo "$response" | grep jobstatus | tail -n 1 | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
    if [[ $jobstatus -eq 2 ]] 
    then
      jobcmd=`echo "$response" | grep cmd | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
      errortext=`echo "$response" | grep errortext`
      failed=1
      echo "job $jobcmd failed, job id is: $jid, due to: $errortext"
    elif [[ $jobstatus -eq 0 ]]
    then
      jobcmd=`echo "$response" | grep cmd | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
      echo "job $jobcmd is pending, job id is: $jid"
      finished=0
      sleep 1 
    fi
  done
  echo "................................................................................................."
done
