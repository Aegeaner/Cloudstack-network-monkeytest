#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian

from common import *
from config import *
import pytest

def test_highlevel_network_single_thread():
	print '=========================Creating Network========================='
	NetworkName = 'Highlevel Network Single Thread'
	args = dict(name=NetworkName, displaytext=DisplayText, networkofferingid=NetworkOfferingId, zoneid=ZoneId)
	result = send_api_request("createNetwork", args)
	error = check_sync_result(result)
	assert(not error)
	if not error:
		NetworkId = result['createnetworkresponse']['network']['id']
		print 'Created Network with id: %s' % NetworkId
	
	print '=========================Deploying VirtualMachine========================='
	args = dict(name='ShowBugTestVM',serviceofferingid=VMServiceOfferingId, templateid=TemplateId, networkids=NetworkId, zoneid=ZoneId)
	result = send_api_request("deployVirtualMachine", args)
	jobid = result['deployvirtualmachineresponse']['jobid']
	async_result = query_async_job(jobid)
	assert(async_result['success'])
	VMId = async_result['queryasyncjobresultresponse']['jobresult']['virtualmachine']['id']
	print 'Created virtual machine with id: {0}'.format(VMId)
	
	print '=========================Associate Ip Address========================='
	args = dict(networkid=NetworkId, zoneid=ZoneId)
	result = send_api_request("associateIpAddress", args)
	jobid = result['associateipaddressresponse']['jobid']
	async_result = query_async_job(jobid)
	IpAddressId = async_result['queryasyncjobresultresponse']['jobresult']['ipaddress']['id']
	print 'Associated Ip Address with id: {0}'.format(IpAddressId)
	
	print '=========================Enabling Static NAT========================='
	args = dict(ipaddressid=IpAddressId, virtualmachineid=VMId)
	result = send_api_request("enableStaticNat", args)
	error = check_sync_result(result)
	assert(not error)
	if error:
		sys.exit()
	
	print '=========================Disabling Static NAT========================='
	args = dict(ipaddressid=IpAddressId)
	result = send_api_request("disableStaticNat", args)
	jobid = result['disablestaticnatresponse']['jobid']
	async_result = query_async_job(jobid)
	assert(async_result['success'])
	
	print '=========================Destroying Virtual Machine========================='
	args = dict(id=VMId, expunge="true")
	result = send_api_request("destroyVirtualMachine", args)
	jobid = result['destroyvirtualmachineresponse']['jobid']
	async_result = query_async_job(jobid)
	assert(async_result['success'])

	print '=========================Disassociate Ip Address========================='
	args = dict(id=IpAddressId)
	result = send_api_request("disassociateIpAddress", args)
	jobid = result['disassociateipaddressresponse']['jobid']
	async_result = query_async_job(jobid)
	assert(async_result['success'])
	
	print '=========================Deleting Network========================='
	args = dict(id=NetworkId)
	result = send_api_request("deleteNetwork", args)
	jobid = result['deletenetworkresponse']['jobid']
	async_result = query_async_job(jobid)
	assert(async_result['success'])

