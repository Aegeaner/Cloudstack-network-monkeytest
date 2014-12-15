#!/usr/bin/python
# -*- coding: utf-8 -*- Author: Guo Jian
import sys 
import time 

from cloudmonkey.cloudmonkey import CloudMonkeyShell
from cloudmonkey.config import config_file

shell = CloudMonkeyShell(sys.argv[0], config_file)

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
			async_result['success'] = True
			break
		elif success == 2:
			print 'Async job [{0}] failed.'.format(cmd)
			async_result['success'] = False
			break
		else:
			print 'Async job [{0}]: Unknown result.'.format(cmd)
			async_result['success'] = False
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

