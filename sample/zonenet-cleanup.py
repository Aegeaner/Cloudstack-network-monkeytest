#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian
import sys
import time

from cloudmonkey.cloudmonkey import CloudMonkeyShell 
from cloudmonkey.config import config_file

ZoneId = 'b9a0dc27-cea5-4602-9bdc-eef68412df46'


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
	
	print '=========================Listing and Deleting Networks========================='
	args = dict(zoneid=ZoneId)
	result = send_api_request("listNetworks", args)
	error = check_sync_result(result)
	if not error:
		Networks = result['listnetworksresponse']['network']
		num = len(Networks)
		for i in range(num):
			if not 'Thread' in Networks[i]['name']:
				continue
			NetworkId = Networks[i]['id']
			print 'Found Network with id: %s' % NetworkId
			args = dict(id=NetworkId, expunge="true")
			result = send_api_request("deleteNetwork", args)
			jobid = result['deletenetworkresponse']['jobid']
			query_async_job(jobid)
		print 'Job Completed successfully.'