#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEI XML Parser

Parse XML text and create output csv with all data necessary for the word list.

Created on Mon Jun 10 16:55:01 2019

@author: christiancasey
"""
#%%

import os
import glob
import pandas

import re
#import treetaggerwrapper

# Local dependencies
from argument_parser import *


# Set the input and output paths
strPathIn = '.' + os.sep + 'epidoc-files'

# Get a list of all texts for processing
# Use command line arguments of the form "file1, file2, file3, etc." when given
# Otherwise, just use all files in the input directory
vFilenames = ParseArguments()
if vFilenames is None:
	vTextFullPaths = glob.glob(strPathIn + os.sep + '*.xml')
else:
	vTextFullPaths = [strPathIn + os.sep + strFilename for strFilename in vFilenames]


vTags = []
vFoobarred = []

# Loop through the list of texts and tag parts of speech
for strTextFullPath in vTextFullPaths:
	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	
	from lxml import etree
	from io import StringIO, BytesIO
	strTextFilename = strTextFullPath.split(os.sep)[-1]
	

	parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
	xmlText = etree.parse(strTextFullPath, parser)
	
#	print(etree.tostring(xmlText.getroot()))
	
	nsmap = {'tei': "http://www.tei-c.org/ns/1.0"}
	
	ns = {'tei': "http://www.tei-c.org/ns/1.0"}
	TEI_NS = "{http://www.tei-c.org/ns/1.0}"
	XML_NS = "{http://www.w3.org/XML/1998/namespace}"
	textLang = xmlText.find('.//' + TEI_NS + 'textLang')
	
	#textLang.attrib['mainLang']
	try:
		strMainLanguage = textLang.attrib['mainLang']
	except:
		strMainLanguage = 'la'

	try:
		strOtherLanguages = textLang.attrib['otherLangs'].strip()	
		if(len(strOtherLanguages) < 2):
			strOtherLanguages = None
			
	except:
		strOtherLanguages = None
		
	
#	print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

	
	
	
	x = xmlText.findall(".//tei:div[@type='edition'][@subtype='transcription']/tei:p", namespaces=nsmap)
	
	if len(x) < 1:
		x = xmlText.findall(".//tei:div[@type='edition'][@subtype='diplomatic']/tei:p", namespaces=nsmap)

	if len(x) < 1:
		print('Error in ' + strTextFilename)
		vFoobarred.append(strTextFilename)
		continue
	
	strXMLText = etree.tostring(x[0], encoding = "unicode")
#	print(strXMLText)
#	print("\n\n\n")
	
	for element in x[0]:
		strTag = element.tag
		strTag = re.sub(TEI_NS, "", strTag)
#		print(strTag)
		vTags.append(strTag)
		

vTags = list(set(vTags))
vTags.sort()		
vFoobarred.sort()















