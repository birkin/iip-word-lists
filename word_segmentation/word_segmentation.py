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
	editionSegmented = copy.deepcopy(x[0])
	editionSegmented.clear()

	strXMLText = etree.tostring(x[0], encoding='utf8', method='xml').decode('utf-8')

	# TODO: Keep orig/reg, abbr, supplied
	# keep foreign xml:lang="heb"

	# remove all <lb>s
	strXMLText = re.sub(r"<lb break=\"no\"(\s*)/>", "", strXMLText)
	strXMLText = re.sub(r"(\s*)<lb break=\"no\"(\s*)/>(\s*)", "", strXMLText)
	strXMLText = re.sub(r"<lb\s*/>", " ", strXMLText)

	# Just delete <note>...</note> right from the start. Shouldn't be there anyway.
	strXMLText = re.sub(r"<note>([^<]*?)</note>", "", strXMLText)

	# Keep stuff as is without worrying about the markup
	# strXMLText = re.sub(r"<supplied>(.*?)</supplied>", r"<w><supplied>\1</supplied></w>", strXMLText)
	# strXMLText = re.sub(r"<supplied (([^>]+|\s)*?)>(.*?)</supplied>", r"<w><supplied>\3</supplied></w>", strXMLText)
	strXMLText = re.sub(r"<supplied>", r"<w><supplied>", strXMLText)
	strXMLText = re.sub(r"<supplied (([^>]+|\s)*?)>", r"<w><supplied \2>", strXMLText)
	strXMLText = re.sub(r"</supplied>", r"</supplied></w>", strXMLText)
	# Supplied

	strXMLText = re.sub(r"<unclear([^>]*?)>(.*?)</unclear>", r"\2", strXMLText)
	# strXMLText = re.sub(r"<hi ([^>]*?)>(.*?)</hi>", r"\2", strXMLText)

	# Discard a bunch of stuff that we don't really care about in this context
	strXMLText = re.sub(r"<([/]*)gap([/]*)>", "", strXMLText)
	strXMLText = re.sub(r"<([/]*)gap ([^>]*?)>", "", strXMLText)
	# strXMLText = re.sub(r"<g ([^>]*?)>([^<]*)</g>", "", strXMLText)
	# strXMLText = re.sub(r"<g>([^<]*)</g>", "", strXMLText)
	# strXMLText = re.sub(r"<g([^>]*?)>", "", strXMLText)
	# strXMLText = re.sub(r"<surplus([^>]*?)>(.*?)</surplus>", "", strXMLText)
	strXMLText = re.sub(r"<orgName>(.*?)</orgName>", "", strXMLText)
	strXMLText = re.sub(r"<([/]*)handShift([^>]*?)>", "", strXMLText)
	# strXMLText = re.sub(r"<unclear([^>]*?)>", "", strXMLText)
	strXMLText = re.sub(r"<space([^>]*?)>", "", strXMLText)

	# Substitutions: <subst> <add>replacement</add> <del>erased</del> </subst>
	strXMLText = re.sub(r"<subst([^>]*?)>(.*?)</subst>", r"\2", strXMLText)
	strXMLText = re.sub(r"<del>(.*?)</del>", r"", strXMLText)
	strXMLText = re.sub(r"<del(([^>]|\s)*?)>(.*?)</del>", r"", strXMLText)
	strXMLText = re.sub(r"<([/]*)del([/]*)>", "", strXMLText)
	strXMLText = re.sub(r"<([/]*)del ([^>]*?)>", "", strXMLText)
	strXMLText = re.sub(r"<add>(.*?)</add>", r"\1", strXMLText)
	strXMLText = re.sub(r"<add(([^>]|\s)*?)>(.*?)</add>", r"\2", strXMLText)

	# Choice: <choice>
	strXMLText = re.sub(r"<choice>(.*?)</choice>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<choice([^>]*?)>(.*?)</choice>", r"§\2§", strXMLText)
	strXMLText = re.sub(r"<([/]*)choice([/]*)>", "", strXMLText)
	strXMLText = re.sub(r"<sic([^>]*?)>(.*?)</sic>", r"", strXMLText)
	strXMLText = re.sub(r"<([/]*)sic([/]*)>", "", strXMLText)
	strXMLText = re.sub(r"<corr([^>]*?)>(.*?)</corr>", r"\2", strXMLText)

	# Orig/Reg
	strXMLText = re.sub(r"<orig([^>]*?)>(.*?)</orig>", r"", strXMLText)
	strXMLText = re.sub(r"<reg([^>]*?)>(.*?)</reg>", r"\2", strXMLText)

	# Deal roughly with word breaks and <foreign ...>
	# Foreign may have one or more words with it
	strXMLText = re.sub(r"<foreign xml\:lang=\"(\w+)\">", r"§", strXMLText)
	strXMLText = re.sub(r"<foreign xml\:lang=\"(\w+(?:-\w+))\">", r"§", strXMLText)
	strXMLText = re.sub(r"<foreign\s*>", r"§", strXMLText)
	strXMLText = re.sub(r"<foreign>", r"§", strXMLText)
	strXMLText = re.sub(r"</foreign>", r"§", strXMLText)

	# Deal with word breaks and <num ...>
	strXMLText = re.sub(r"<num([^>]*?)>", r"§", strXMLText)
	strXMLText = re.sub(r"</num>", r"§", strXMLText)

	# Deal with <expan>
	# strXMLText = re.sub(r"<expan>(.*?)</expan>", r"<w><expan>\1</expan></w>", strXMLText)
	# strXMLText = re.sub(r"<expan([^>]*?)>(.*?)</expan>", r"<w><expan \1>\2</expan></w>", strXMLText)
	strXMLText = re.sub(r"(\s*)<expan([^>]*?)>", r"<w><expan \1>", strXMLText)
	strXMLText = re.sub(r"</expan>(\s*)", r"</expan></w>", strXMLText)
	#
	# strXMLText = re.sub(r"<abbr>(.*?)</abbr>", r"§\1", strXMLText)
	# strXMLText = re.sub(r"<([/]*)abbr([/]*)>", "", strXMLText)

	# Deal with <app>
	strXMLText = re.sub(r"<app>(.*?)</app>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<app([^>]*)>(.*?)</app>", r"\2", strXMLText)
	strXMLText = re.sub(r"<lem>(.*?)</lem>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<lem ([^>]*?)>(.*?)</lem>", r"§\2§", strXMLText)
	strXMLText = re.sub(r"<rdg>(.*?)</rdg>", r"§ª\1§", strXMLText)

	# Normalized

	# Expanding abbreviations and such
	# strXMLText = re.sub(r"<am>(.*?)</am>", r"", strXMLText)
	# strXMLText = re.sub(r"<am/>", r"", strXMLText)
	# strXMLText = re.sub(r"<ex>(.*?)</ex>", r"\1§", strXMLText)
	# strXMLText = re.sub(r"<ex ([^>]*?)>(.*?)</ex>", r"\2§", strXMLText)

	# Replace all spaces as word breaks
	# strXMLText = re.sub(r"\s+", "§", strXMLText)
	# strXMLText = re.sub(r"[\.\,\;‧·⋅•∙]", "§", strXMLText)
	# strXMLText = re.sub(r"§\?§", "§", strXMLText)


	# TEMP ELIMINATE FOREIGN AND NUM
	# strXMLText = re.sub(r"<foreign([^>]*?)>(.*?)</foreign>", r"\2", strXMLText)
	# strXMLText = re.sub(r"<num([^>]*?)>(.*?)</num>", r"\2", strXMLText)
	# strXMLText = re.sub(r"<num>(.*?)</num>", r"\1", strXMLText)


	# Collapse word breaks and reinstate line breaks
	# strXMLText = re.sub(r"¶", "\n", strXMLText)    # Reinstate line breaks
	strXMLText = re.sub(r"§+", "§", strXMLText)    # Finally, collapse word breaks
	# strXMLText = re.sub(r"§¶§", "§¶", strXMLText)  # Only one word break with line break

	# With all tags removed, discard any remaining quotes
	# strXMLText = re.sub(r"\"", "", strXMLText)

	strXMLText = re.sub(r"§", " ", strXMLText)    # Finally, collapse word breaks
	editionInput = etree.XML(strXMLText, parser)

	# iterate through both text and element nodes of the <p> element
	for node in editionInput.xpath("child::node()"):
		# Strategies for segmenting words:
		if type(node) == etree._ElementUnicodeResult:
			node = node.strip()
			node = re.sub(r"[\.\,\;‧·⋅•∙]", "", node)

			# Segment words on just the spaces
			words = [word for word in node.split(" ") if len(word.strip())]

			# Add word child elems
			for i, word in enumerate(words):
				wordElem = etree.SubElement(editionSegmented, '{http://www.tei-c.org/ns/1.0}w')
				wordElem.text = word.strip()
				if i < len(words) - 1:
					wordElem.tail = " "
		else:
			node.tail = ''
			if node.tag == '{http://www.tei-c.org/ns/1.0}w':
				editionSegmented.append(node)
			elif node.tag == '{http://www.tei-c.org/ns/1.0}num':
				editionSegmented.append(node)


	wordElems = editionSegmented.findall(".//tei:w", namespaces=nsmap)
	for i, wordElem in enumerate(wordElems):
		wordElem.attrib[XML_NS + 'id'] = '{}-{}'.format(os.path.splitext(strTextFilename)[0], i + 1)
		wordElem.attrib[XML_NS + 'lang'] = strMainLanguage

	# make new transcription segmented element and append our segmented edition to that
	body = xmlText.find(".//tei:body", namespaces=nsmap)
	transcription = xmlText.find(".//tei:div[@type='edition'][@subtype='transcription']", namespaces=nsmap)
	transcriptionSegmented = copy.deepcopy(transcription)
	transcriptionSegmented.clear()
	transcriptionSegmented.attrib['type'] = "edition"
	transcriptionSegmented.attrib['subtype'] = "transcription_segmented"

	editionSegmented.tail = "\n"
	transcriptionSegmented.append(editionSegmented)
	transcriptionSegmented.tail = "\n"
	body.append(transcriptionSegmented)


	# Skip it if the text has no textual content,
	if len(x) < 1:
		# print('Error in ' + strTextFilename)
		vFoobarred.append(strTextFilename)
		continue

	xmlData = etree.tostring(xmlText, encoding='utf-8', pretty_print=False, xml_declaration=True)
	file = open(strPathOut + os.sep + strTextFilename, "wb")
	file.write(xmlData)

	# strXMLText = re.sub(r"<lb break=\"no\"(\s*)/>", "¶", strXMLText)
