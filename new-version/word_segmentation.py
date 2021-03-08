#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
word_segmentation.py

Segment words from the XML files with <w> elements and export a CSV of words

"""

import os
import glob
import re
import copy
import pdb
from lxml import etree


# Local dependencies
from argument_parser import *


# Set the input and output paths
strPathIn = '.' + os.sep + 'word_segmentation_files_in'
strPathOut = '.' + os.sep + 'word_segmentation_files_out'

# Get a list of all texts for processing
# Use command line arguments of the form "file1, file2, file3, etc." when given
# Otherwise, just use all files in the input directory
bClearFolder = False
vFilenames = ParseArguments()
if vFilenames is None:
	vTextFullPaths = glob.glob(strPathIn + os.sep + '*.xml')
	vTextFullPaths.sort()
	bClearFolder = True
else:
	vTextFullPaths = [strPathIn + os.sep + strFilename for strFilename in vFilenames]

vTextFullPaths.sort()

strTextsAll = ""
strExtraCharacters = ""

vNoLang = []
vLangs = []
vFoobarred = []

vAllowedLangs = [ 'arc', 'grc', 'he', 'la' ]

# Loop through the list of texts, parse XML, make data frames, save as CSV
for strTextFullPath in vTextFullPaths:
	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strTextFullPath.split(os.sep)[-1]

	# Current parser options clean up redundant namespace declarations and remove patches of whitespace
	# For more info, see "Parser Options" in: https://lxml.de/parsing.html
	parser = etree.XMLParser(ns_clean=True, remove_blank_text=False)
	xmlText = etree.parse(strTextFullPath, parser)

	nsmap = {'tei': "http://www.tei-c.org/ns/1.0"}

	ns = {'tei': "http://www.tei-c.org/ns/1.0"}
	TEI_NS = "{http://www.tei-c.org/ns/1.0}"
	XML_NS = "{http://www.w3.org/XML/1998/namespace}"
	textLang = xmlText.find('.//' + TEI_NS + 'textLang')

	# Get text-wide language settings
	strMainLanguage = ''
	try:
		strMainLanguage = textLang.attrib['mainLang']
	except:
		vNoLang.append(strTextFilename)
		strMainLanguage = 'grc'
		continue

	# Find cases where language code is wrong
	if strMainLanguage not in vAllowedLangs:
		print("Error, invalid language (%s) in %s" % (strMainLanguage, strTextFilename))
		continue


	vLangs.append(strMainLanguage)

	try:
		strOtherLanguages = textLang.attrib['otherLangs'].strip()
		if(len(strOtherLanguages) < 2):
			strOtherLanguages = None

	except:
		strOtherLanguages = None

	x = xmlText.findall(".//tei:div[@type='edition'][@subtype='transcription']/tei:p", namespaces=nsmap)


	# Skip it if the text has no textual content,
	if len(x) < 1:
		# print('Error in ' + strTextFilename)
		vFoobarred.append(strTextFilename)
		continue

	# Get script/language from attribute on <p> when it exists
	# Right now this is unused, according to TEI, defines script (which is already obvious)
	if XML_NS + 'lang' in x[0].attrib:
		strPLanguage = x[0].attrib[XML_NS + 'lang']

	words = []
	edition = copy.deepcopy(x[0])
	edition.clear()

	# iterate through both text and element nodes of the <p> element
	for node in x[0].xpath("child::node()"):

		# Strategies for segmenting words:
		if type(node) == etree._ElementUnicodeResult:
			node = node.strip()

			# Segment words on just the spaces
			words = node.split(" ")

			# Add word child elems
			for word in words:
				if len(word):
					word_elem = etree.SubElement(edition, 'w')
					word_elem.text = word
					word_elem.tail = " "
		else:
			node_copy = copy.deepcopy(node)

			if node.tag == '{http://www.tei-c.org/ns/1.0}lb':
				edition.insert(0, node_copy)
			elif node.tag == '{http://www.tei-c.org/ns/1.0}expan':
				# turn it into a word by throwing away all the tags
				# or could turn it into two words

				# or could ignore and surround it with w
				edition.insert(0, node_copy)

			elif node.tag == '{http://www.tei-c.org/ns/1.0}choice':
				# or could ignore and surround it with w
				edition.insert(0, node_copy)

			elif node.tag == '{http://www.tei-c.org/ns/1.0}abbr':
				# or could ignore and surround it with w
				edition.insert(0, node_copy)

			else:
				edition.insert(0, node_copy)


	body = xmlText.find(".//tei:body", namespaces=nsmap)
	transcription_segmented = etree.SubElement(body, 'div')
	transcription_segmented.attrib['subtype'] = "transcription_segmented"
	transcription_segmented.append(edition)


	# Skip it if the text has no textual content,
	if len(x) < 1:
		# print('Error in ' + strTextFilename)
		vFoobarred.append(strTextFilename)
		continue

	xmlData = etree.tostring(xmlText, encoding='utf-8', pretty_print=False, xml_declaration=True)
	file = open(strPathOut + os.sep + strTextFilename, "wb")
	file.write(xmlData)

	# strXMLText = re.sub(r"<lb break=\"no\"(\s*)/>", "¶", strXMLText)
