#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
word_segmentation.py

Segment words from the XML files with <w> elements and export a CSV of words

DISCLAIMER - this is a prototype and not meant to be used in production 


"""

import os
import glob
import re
import copy
import csv
import collections
from lxml import etree


# Local dependencies
from argument_parser import *


# Set the input and output paths
strPathIn = '.' + os.sep + 'word_segmentation_files_in'
strPathOut = '.' + os.sep + 'word_segmentation_files_out'
strPathListOut = '.' + os.sep + 'word_segmentation_lists'

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

vAllowedLangs = [ 'arc', 'grc', 'he', 'la', 'x-unknown', 'syc', 'phn', 'xcl', 'Other', 'geo']
transformationErrors = 0

# Loop through the list of texts, parse XML, make data frames, save as CSV
for strTextFullPath in vTextFullPaths:

	# bypass the xxx inscriptions
	if "xxx" in strTextFullPath:
		continue

	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strTextFullPath.split(os.sep)[-1]

	# Current parser options clean up redundant namespace declarations and remove patches of whitespace
	# For more info, see "Parser Options" in: https://lxml.de/parsing.html
	parser = etree.XMLParser(ns_clean=True, remove_blank_text=False)

	try:
		xmlText = etree.parse(strTextFullPath, parser)
	except Exception as e:
		print('#' * 20)
		print('Error with parsing text as XML:')
		print(e)
		print(strTextFilename)
		print('#' * 20)
		transformationErrors += 1
		continue

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

	try:
		words = []
		editionSegmented = copy.deepcopy(x[0])
		editionSegmented.clear()

		strXMLText = etree.tostring(x[0], encoding='utf8', method='xml').decode('utf-8')

		# remove all <lb>s
		strXMLText = re.sub(r"<lb break=\"no\"(\s*)/>", "", strXMLText)
		strXMLText = re.sub(r"(\s*)<lb break=\"no\"(\s*)/>(\s*)", "", strXMLText)
		strXMLText = re.sub(r"<lb\s*/>", " ", strXMLText)

		# Just delete <note>...</note> right from the start. Shouldn't be there anyway.
		strXMLText = re.sub(r"<note>([^<]*?)</note>", "", strXMLText)

		# Discard a bunch of stuff that we don't really care about in this context
		strXMLText = re.sub(r"<([/]*)gap([/]*)>", "", strXMLText)
		strXMLText = re.sub(r"<([/]*)gap ([^>]*?)>", "", strXMLText)
		strXMLText = re.sub(r"<orgName>(.*?)</orgName>", "", strXMLText)
		strXMLText = re.sub(r"<([/]*)handShift([^>]*?)>", "", strXMLText)
		strXMLText = re.sub(r"<space([^>]*?)>", "", strXMLText)
		strXMLText = re.sub(r"<sic([^>]*?)>(.*?)</sic>", r"", strXMLText)
		strXMLText = re.sub(r"<([/]*)sic([/]*)>", "", strXMLText)
		strXMLText = re.sub(r"<corr([^>]*?)>(.*?)</corr>", r"\2", strXMLText)

		# Deal with <app>
		strXMLText = re.sub(r"<app>(.*?)</app>", r"§\1§", strXMLText)
		strXMLText = re.sub(r"<app([^>]*)>(.*?)</app>", r"\2", strXMLText)
		strXMLText = re.sub(r"<lem>(.*?)</lem>", r"§\1§", strXMLText)
		strXMLText = re.sub(r"<lem ([^>]*?)>(.*?)</lem>", r"§\2§", strXMLText)
		strXMLText = re.sub(r"<rdg>(.*?)</rdg>", r"§ª\1§", strXMLText)

		# Substitutions: <subst> <add>replacement</add> <del>erased</del> </subst>
		strXMLText = re.sub(r"<subst([^>]*?)>(.*?)</subst>", r"\2", strXMLText)
		strXMLText = re.sub(r"<del>(.*?)</del>", r"", strXMLText)
		strXMLText = re.sub(r"<del(([^>]|\s)*?)>(.*?)</del>", r"", strXMLText)
		strXMLText = re.sub(r"<([/]*)del([/]*)>", "", strXMLText)
		strXMLText = re.sub(r"<([/]*)del ([^>]*?)>", "", strXMLText)
		strXMLText = re.sub(r"<add>(.*?)</add>", r"\1", strXMLText)
		strXMLText = re.sub(r"<add(([^>]|\s)*?)>(.*?)</add>", r"\2", strXMLText)

		# Supplied, Orig/Reg, expan, abbr, unclear, hi, choice
		strXMLText = re.sub(r'<supplied reason="\w+"/>', '', strXMLText)
		strXMLText = re.sub(r'(\s+)<supplied([^>]*?)>(.*?)</supplied>(\s+)', r"\1<w><supplied \2>\3</supplied></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<supplied([^>]*?)>(.*?)</supplied>(\s+)', r"<w><supplied \1>\2</supplied></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<supplied([^>]*?)>(.*?)</supplied>^\s+', r"\1<w><supplied \2>\3</supplied></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<reg([^>]*?)>(.*?)</reg>(\s+)', r"\1<w><reg \2>\3</reg></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<reg([^>]*?)>(.*?)</reg>(\s+)', r"<w><reg \1>\2</reg></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<reg([^>]*?)>(.*?)</reg>^\s+', r"\1<w><reg \2>\3</reg></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<expan([^>]*?)>(.*?)</expan>(\s+)', r"\1<w><expan \2>\3</expan></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<expan([^>]*?)>(.*?)</expan>(\s+)', r"<w><expan \1>\2</expan></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<expan([^>]*?)>(.*?)</expan>^\s+', r"\1<w><expan \2>\3</expan></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<abbr([^>]*?)>(.*?)</abbr>(\s+)', r"\1<w><abbr \2>\3</abbr></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<abbr([^>]*?)>(.*?)</abbr>(\s+)', r"<w><abbr \1>\2</abbr></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<abbr([^>]*?)>(.*?)</abbr>^\s+', r"\1<w><abbbr \2>\3</abbr></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<unclear([^>]*?)>(.*?)</unclear>(\s+)', r"\1<w><unclear \2>\3</unclear></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<unclear([^>]*?)>(.*?)</unclear>(\s+)', r"<w><unclear \1>\2</unclear></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<unclear([^>]*?)>(.*?)</unclear>^\s+', r"\1<w><unclear \2>\3</unclear></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<hi([^>]*?)>(.*?)</hi>(\s+)', r"\1<w><hi \2>\3</hi></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<hi([^>]*?)>(.*?)</hi>(\s+)', r"<w><hi \1>\2</hi></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<hi([^>]*?)>(.*?)</hi>^\s+', r"\1<w><hi \2>\3</hi></w>", strXMLText)

		strXMLText = re.sub(r'(\s+)<choice([^>]*?)>(.*?)</choice>(\s+)', r"\1<w><choice \2>\3</choice></w>\4", strXMLText)
		strXMLText = re.sub(r'^\s+<choice([^>]*?)>(.*?)</choice>(\s+)', r"<w><choice \1>\2</choice></w>\3", strXMLText)
		strXMLText = re.sub(r'(\s+)<choice([^>]*?)>(.*?)</choice>^\s+', r"\1<w><choice \2>\3</choice></w>", strXMLText)


		strXMLText = re.sub(r"§+", "§", strXMLText)
		strXMLText = re.sub(r"§", " ", strXMLText)

		editionInput = etree.XML(strXMLText, parser)
	except Exception as e:

		print('#' * 20)
		print('Error with parsing edition as XML:')
		print(e)
		print(strTextFullPath)
		print(strXMLText)
		print('#' * 20)

		transformationErrors += 1

		continue

	# iterate through both text and element nodes of the <p> element
	for node in editionInput.xpath("child::node()"):
		# Strategies for segmenting words:
		if type(node) == etree._ElementUnicodeResult:
			node = node.strip()
			node = re.sub(r"[\.\,\;‧·⋅•∙]", "", node)
			node = re.sub(r"\d+", "", node)
			node = node.replace("_", "")
			node = node.replace("*", "")
			node = node.replace("+", "")
			node = node.replace("'", "")
			node = node.replace(":", "")
			node = node.replace("\"", "")
			node = node.replace("ʹ", "")
			node = node.replace("´", "")
			node = node.replace("ֿ", "") # The niqqud point rafe

			# Segment words on just the spaces
			words = [word for word in node.split(" ") if len(word.strip())]

			# Add word child elems
			for i, word in enumerate(words):
				wordElem = etree.SubElement(editionSegmented, '{http://www.tei-c.org/ns/1.0}w')
				wordElem.text = "".join(word.split())
				if i < len(words) - 1:
					wordElem.tail = " "
		else:
			node.tail = ''
			if node.tag == '{http://www.tei-c.org/ns/1.0}w':
				editionSegmented.append(node)
			elif node.tag == '{http://www.tei-c.org/ns/1.0}num':
				editionSegmented.append(node)


	## all child nodes should have ids
	wordElems = editionSegmented.findall(".//tei:w", namespaces=nsmap)
	for i, wordElem in enumerate(wordElems):
		wordElem.attrib[XML_NS + 'id'] = '{}-{}'.format(os.path.splitext(strTextFilename)[0], i + 1)
		has_foreign_elem = False
		for child in wordElem:
			if child.tag == '{http://www.tei-c.org/ns/1.0}supplied' and XML_NS + 'lang' in child.attrib:
				wordElem.attrib[XML_NS + 'lang'] = child.attrib[XML_NS + 'lang']
				has_foreign_elem = True
		if not has_foreign_elem:
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

# Read all segmented files for processing word lists
vSegmentedTexts = glob.glob(strPathOut + os.sep + '*.xml')
vSegmentedTexts.sort()

WORD_LISTS = {}
WORD_COUNT = 0

# Loop through texts building lists
for strSegmentedTextFullPath in vSegmentedTexts:

	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strSegmentedTextFullPath.split(os.sep)[-1]

	# Current parser options clean up redundant namespace declarations and remove patches of whitespace
	# For more info, see "Parser Options" in: https://lxml.de/parsing.html
	parser = etree.XMLParser(ns_clean=True, remove_blank_text=False)
	xmlText = etree.parse(strSegmentedTextFullPath, parser)
	wordElems = xmlText.findall(".//tei:div[@type='edition'][@subtype='transcription_segmented']/tei:p/tei:w", namespaces=nsmap)
	WORD_COUNT += len(wordElems)

	# Build word lists by language
	for wordElem in wordElems:
		# serialize the word elems to text
		wordElemText = etree.tostring(wordElem, encoding='utf8', method='xml').decode('utf-8').strip()
		wordElemText = wordElemText.replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
		wordElemText = wordElemText.replace('xmlns:xi="http://www.w3.org/2001/XInclude"', "")

		# check if <num> elem is in text (quick method)
		wordIsNum = 0
		if "<num" in wordElemText:
			wordIsNum = 1

		# add version to unique/alphabetize on
		normalized = ''.join(wordElem.itertext()).strip()

		if wordElemText and len(wordElemText):
			wordParams = wordElem.attrib[XML_NS + 'id'].split('-')
			text = "{}.xml".format(wordParams[0])
			wordNumber = wordParams[1]

			if wordElem.attrib[XML_NS + 'lang'] in WORD_LISTS:
				WORD_LISTS[wordElem.attrib[XML_NS + 'lang']].append([text, wordNumber, normalized, wordElem.attrib[XML_NS + 'lang'], wordIsNum])
			else:
				WORD_LISTS[wordElem.attrib[XML_NS + 'lang']] = [[text, wordNumber, normalized, wordElem.attrib[XML_NS + 'lang'], wordIsNum]]



# Write word lists to CSV files
for lang in WORD_LISTS:

	# write to file
	with open(strPathListOut + '/word_list_{}.csv'.format(lang.lower()), 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		for word_row in WORD_LISTS[lang]:
			csvwriter.writerow(word_row)

print("#" * 20)
print("#" * 20)
print("Total word count:")
print(WORD_COUNT)
print("Transformation errors:")
print(transformationErrors)
print("#" * 20)
