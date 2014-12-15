#!/bin/bash

shopt -s expand_aliases
alias CM_CUSTOM='cloudmonkey -c /root/.cloudmonkey/config_gj'

CM_CUSTOM set asyncblock false

volumeids=`CM_CUSTOM list volumes filter=id | grep id | awk '{ gsub(/"/,"",$NF); gsub(/,/,"",$NF); print $NF }' `
for volumeid in $volumeids
do
    echo "Destroying volume with id: $volumeid"
    CM_CUSTOM delete volume id=$volumeid 1>/dev/null
done

