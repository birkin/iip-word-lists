#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run language-specific external lemmatizer and return the results

Created on Tuesday, June 25, 2019

@author: christiancasey
"""


import docker

def Lemmatize(strWord, strLanguage):
	
	strResults = ''
	
	# Lemmatize Latin
	if strLanguage == 'la':
		client = docker.from_env()
		container = client.containers.run('perseidsproject/morpheus-perseids', '/bin/bash', detach=True, tty=True)#, stdin_open=True)
		strResults = container.exec_run('sh -c "MORPHLIB=stemlib bin/morpheus -L -S \'%s\'"' % strWord).output.decode('utf-8')
		container.stop()
	
	return strResults