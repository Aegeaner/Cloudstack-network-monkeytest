#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian
import sys
import time
import datetime
import thread

from cloudmonkey.cloudmonkey import CloudMonkeyShell 
from cloudmonkey.config import config_file

NetworkOfferingId = '8d648af4-ceb9-4640-bded-7e2ce3a7a699'
ZoneId = 'b9a0dc27-cea5-4602-9bdc-eef68412df46'
VMServiceOfferingId = '12e34e93-e786-48f6-a66c-8b3f9aa3e0ff'
TemplateId = '7f233e45-c9de-40d7-900e-496758ee3c50'
DisplayText = 'Just a test.'

shell = CloudMonkeyShell(sys.argv[0], config_file)

def thread_print(threadName, str):
		print '<{0}>: {1}'.format(threadName, str)

def send_api_request(apiname, args):
	isasync = False
        if 'asyncapis' in shell.apicache:
            isasync = apiname in shell.apicache['asyncapis']
	result = shell.make_request(apiname, args)
	if result is None:
            sys.exit()
	return result

def query_async_job(threadName, jobid):
	args = dict(jobid = jobid)
	while True:
		async_result = send_api_request("queryAsyncJobResult", args)
		cmd = async_result['queryasyncjobresultresponse']['cmd']
		success = async_result['queryasyncjobresultresponse']['jobstatus']
		if success == 0:
			continue
		elif success == 1:
			thread_print(threadName, 'Async job [{0}] is successful.'.format(cmd))
			break
		elif success == 2:
			jobresult = async_result['queryasyncjobresultresponse']['jobresult']
			thread_print(threadName, 'Async job [{0}] failed due to {1}.'.format(cmd, jobresult))
			break
		else:
			thread_print(threadName, 'Async job [{0}]: Unknown result.'.format(cmd))
			break
		time.sleep(5)
	return async_result

def check_sync_result(threadName, sync_response):
	error = sync_response.has_key('errorcode')
	if error == True:
		thread_print(threadName, 'Sync job failed.')
	else:
		thread_print(threadName, 'Sync job successful.')
	return error

def test_case(threadName):
	thread_print(threadName, '=========================Creating Network=========================')
	NetworkName = "{0}-{1}-{2}".format(threadName, "Network", datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
	args = dict(name=NetworkName, displaytext=DisplayText, networkofferingid=NetworkOfferingId, zoneid=ZoneId)
	result = send_api_request("createNetwork", args)
	error = check_sync_result(threadName, result)
	if not error:
		NetworkId = result['createnetworkresponse']['network']['id']
		thread_print(threadName, 'Created Network with id: %s' % NetworkId)
	
	thread_print(threadName, '=========================Deploying VirtualMachine=========================')
	VMName = "{0}-{1}-{2}".format(threadName, "VM", datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
	args = dict(name=VMName, serviceofferingid=VMServiceOfferingId, templateid=TemplateId, networkids=NetworkId, zoneid=ZoneId)
	result = send_api_request("deployVirtualMachine", args)
	jobid = result['deployvirtualmachineresponse']['jobid']
	async_result = query_async_job(threadName, jobid)
	VMId = async_result['queryasyncjobresultresponse']['jobresult']['virtualmachine']['id']
	thread_print(threadName, 'Created virtual machine with id: {0}'.format(VMId))
	
	thread_print(threadName, '=========================Associate Ip Address=========================')
	args = dict(networkid=NetworkId, zoneid=ZoneId)
	result = send_api_request("associateIpAddress", args)
	jobid = result['associateipaddressresponse']['jobid']
	async_result = query_async_job(threadName, jobid)
	IpAddressId = async_result['queryasyncjobresultresponse']['jobresult']['ipaddress']['id']
	thread_print(threadName, 'Associated Ip Address with id: {0}'.format(IpAddressId))
	
	thread_print(threadName, '=========================Enabling Static NAT=========================')
	args = dict(ipaddressid=IpAddressId, virtualmachineid=VMId)
	result = send_api_request("enableStaticNat", args)
	error = check_sync_result(threadName, result)
	if error:
		sys.exit()
	
	thread_print(threadName, '=========================Disabling Static NAT=========================')
	args = dict(ipaddressid=IpAddressId)
	result = send_api_request("disableStaticNat", args)
	jobid = result['disablestaticnatresponse']['jobid']
	query_async_job(threadName, jobid)
	
	thread_print(threadName, '=========================Destroying Virtual Machine=========================')
	args = dict(id=VMId, expunge="true")
	result = send_api_request("destroyVirtualMachine", args)
	jobid = result['destroyvirtualmachineresponse']['jobid']
	query_async_job(threadName, jobid)
	
	thread_print(threadName, '=========================Disassociate Ip Address=========================')
	args = dict(id=IpAddressId)
	result = send_api_request("disassociateIpAddress", args)
	jobid = result['disassociateipaddressresponse']['jobid']
	query_async_job(threadName, jobid)
	
	thread_print(threadName, '=========================Deleting Network=========================')
	args = dict(id=NetworkId)
	result = send_api_request("deleteNetwork", args)
	jobid = result['deletenetworkresponse']['jobid']
	query_async_job(threadName, jobid)

def start_test():
	try:
		for i in range(15):
			thread.start_new_thread(test_case, ("Thread-{0}".format(i),))

	except:
		print "Error: unable to start thread"
	while 1:
		pass
	
if __name__ == '__main__':
	start_test()
	

	
	

