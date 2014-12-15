#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian
import sys
import time

from cloudmonkey.cloudmonkey import CloudMonkeyShell 
from cloudmonkey.config import config_file

NetworkOfferingId = '8d648af4-ceb9-4640-bded-7e2ce3a7a699'
ZoneId = 'b9a0dc27-cea5-4602-9bdc-eef68412df46'
VMServiceOfferingId = '12e34e93-e786-48f6-a66c-8b3f9aa3e0ff'
TemplateId = '7f233e45-c9de-40d7-900e-496758ee3c50'
DisplayText = 'Just a test.'

def send_api_request(apiname, args):
	isasync = False
        if 'asyncapis' in shell.apicache:
            isasync = apiname in shell.apicache['asyncapis']
	result = shell.make_request(apiname, args)
	if result is None:
            sys.exit()
	return result

def query_async_job(jobid):
	args = dict(jobid = jobid)
	while True:
		async_result = send_api_request("queryAsyncJobResult", args)
		cmd = async_result['queryasyncjobresultresponse']['cmd']
		success = async_result['queryasyncjobresultresponse']['jobstatus']
		if success == 0:
			continue
		elif success == 1:
			print 'Async job [{0}] is successful.'.format(cmd)
			break
		elif success == 2:
			print 'Async job [{0}] failed.'.format(cmd)
			break
		else:
			print 'Async job [{0}]: Unknown result.'.format(cmd)
			break
		time.sleep(5)
	return async_result

def check_sync_result(sync_response):
	error = sync_response.has_key('errorcode')
	if error == True:
		print 'Sync job failed.'
	else:
		print 'Sync job successful.'
	return error

if __name__ == '__main__':
	shell = CloudMonkeyShell(sys.argv[0], config_file)	
	
	print '=========================Creating Network========================='
	NetworkName = raw_input('Please input you want to name of the network:')
	args = dict(name=NetworkName, displaytext=DisplayText, networkofferingid=NetworkOfferingId, zoneid=ZoneId)
	result = send_api_request("createNetwork", args)
	error = check_sync_result(result)
	if not error:
		NetworkId = result['createnetworkresponse']['network']['id']
		print 'Created Network with id: %s' % NetworkId
	
	print '=========================Deploying VirtualMachine========================='
	args = dict(serviceofferingid=VMServiceOfferingId, templateid=TemplateId, networkids=NetworkId, zoneid=ZoneId)
	result = send_api_request("deployVirtualMachine", args)
	jobid = result['deployvirtualmachineresponse']['jobid']
	async_result = query_async_job(jobid)
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
	if error:
		sys.exit()
	
	print '=========================Disabling Static NAT========================='
	args = dict(ipaddressid=IpAddressId)
	result = send_api_request("disableStaticNat", args)
	jobid = result['disablestaticnatresponse']['jobid']
	query_async_job(jobid)
	
	print '=========================Destroying Virtual Machine========================='
	args = dict(id=VMIdVMId, expunge="true")
	result = send_api_request("destroyVirtualMachine", args)
	jobid = result['destroyvirtualmachineresponse']['jobid']
	query_async_job(jobid)
	
	print '=========================Disassociate Ip Address========================='
	args = dict(id=IpAddressId)
	result = send_api_request("disassociateIpAddress", args)
	jobid = result['disassociateipaddressresponse']['jobid']
	query_async_job(jobid)
	
	print '=========================Deleting Network========================='
	args = dict(id=NetworkId)
	result = send_api_request("deleteNetwork", args)
	jobid = result['deletenetworkresponse']['jobid']
	query_async_job(jobid)
	
	

