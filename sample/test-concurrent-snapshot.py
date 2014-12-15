#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian
import sys
import time
import datetime
import thread

from cloudmonkey.cloudmonkey import CloudMonkeyShell 
from cloudmonkey.config import config_file

NetworkOfferingId = 'a4e744b7-b37f-4687-a04a-6139ebb8a947'
ZoneId = '9890edd5-f24b-4dcb-85f0-a03f936c1269'
VMServiceOfferingId = 'aa241bf2-3f21-43a2-95a6-0263437d4eef'
TemplateId = '4364e1a4-53b6-4cd4-bc62-17edd71ca62c'
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

def test_case(threadName, NetworkId):
	thread_print(threadName, '=========================Deploying VirtualMachine=========================')
	VMName = "{0}-{1}-{2}".format(threadName, "VM", datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
	args = dict(name=VMName, serviceofferingid=VMServiceOfferingId, templateid=TemplateId, networkids=NetworkId, zoneid=ZoneId)
	result = send_api_request("deployVirtualMachine", args)
	jobid = result['deployvirtualmachineresponse']['jobid']
	async_result = query_async_job(threadName, jobid)
	VMId = async_result['queryasyncjobresultresponse']['jobresult']['virtualmachine']['id']
	thread_print(threadName, 'Created virtual machine with id: {0}'.format(VMId))
	
	thread_print(threadName, '=========================Listing Volumes=========================')
	args = dict(virtualmachineid=VMId)
	result = send_api_request("listVolumes", args)
	error = check_sync_result(threadName, result)
	if not error:
		rootVolumeId = result['listvolumesresponse']['volume'][0]['id']
		thread_print(threadName, 'List root volume with id: %s' % rootVolumeId)

	thread_print(threadName, '=========================Creating Snapshot=========================')
	args = dict(volumeid=rootVolumeId)
	result = send_api_request("createSnapshot", args)
	jobid = result['createsnapshotresponse']['jobid']
	query_async_job(threadName, jobid)
	
	thread_print(threadName, '=========================Listing Snapshot=========================')
	args = dict(volumeid=rootVolumeId)
	result = send_api_request("listSnapshots", args)
	error = check_sync_result(threadName, result)
	if not error:
		snapshotName = result['listsnapshotsresponse']['snapshot'][0]['name']
		snapshotId = result['listsnapshotsresponse']['snapshot'][0]['id']
		thread_print(threadName, 'List Snapshot: {0} with id: {1}'.format(snapshotName, snapshotId))
		
	thread_print(threadName, '=========================Deleting Snapshot=========================')
	args = dict(id=snapshotId)
	result = send_api_request("deleteSnapshot", args)
	jobid = result['deletesnapshotresponse']['jobid']
	query_async_job(threadName, jobid)
	
	thread_print(threadName, '=========================Listing Snapshot=========================')
	args = dict(id=snapshotId)
	result = send_api_request("listSnapshots", args)
	error = check_sync_result(threadName, result)
	if not error:
		snapshot = result['listsnapshotsresponse']
		thread_print(threadName, 'List Snapshot: \n%s' % snapshot)
	else:
		thread_print("The snapshot has been deleted.")
	
	thread_print(threadName, '=========================Destroying Virtual Machine=========================')
	args = dict(id=VMId, expunge="true")
	result = send_api_request("destroyVirtualMachine", args)
	jobid = result['destroyvirtualmachineresponse']['jobid']
	query_async_job(threadName, jobid)
	
def start_test():
	print('=========================Creating Network=========================')
	NetworkName = "{0}-{1}".format("ThreadTestSnapshot", datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
	args = dict(name=NetworkName, displaytext=DisplayText, networkofferingid=NetworkOfferingId, zoneid=ZoneId)
	result = send_api_request("createNetwork", args)
	error = check_sync_result('global', result)
	if not error:
		NetworkId = result['createnetworkresponse']['network']['id']
		thread_print('global', 'Created Network with id: %s' % NetworkId)
		
	try:
		for i in range(15):
			thread.start_new_thread(test_case, ("Thread-{0}".format(i), NetworkId,))

	except:
		print "Error: unable to start thread"
	while 1:
		pass

if __name__ == '__main__':
	start_test()
