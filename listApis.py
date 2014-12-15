#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: Guo Jian

from common import *
from config import *

def list_apis():
	args = None
	result = send_api_request("listApis", args)
	error = check_sync_result(result)
	assert(not error)
	if not error:
		response = result['listapisresponse']
		file = open('ApiCache.txt', 'w')
		file.write(str(response))
		file.close()

if __name__ == '__main__':
	list_apis()
