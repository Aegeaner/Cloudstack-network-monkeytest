#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'
#alias CM_CUSTOM='cloudmonkey'

jobids=`CM_CUSTOM list asyncjobs domainid=2 account=guojian filter=jobid | grep jobid | awk '{ gsub(/"/,"",$NF); print $NF }'`
for jobid in $jobids
do
    response=`CM_CUSTOM query asyncjobresult jobid=$jobid`
    jobstatus=`echo "$response" | grep jobstatus | tail -n 1 | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
    if [ $jobstatus -eq 2 ] 
    then
      jobcmd=`echo "$response" | grep cmd | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
      errortext=`echo "$response" | grep errortext`
      echo "job $jobcmd failed, job id is: $jobid, due to: $errortext"
    elif [ $jobstatus -eq 0 ]
    then
      jobcmd=`echo "$response" | grep cmd | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }'`
      echo "job $jobcmd is pending, job id is: $jobid" 
    fi
done

