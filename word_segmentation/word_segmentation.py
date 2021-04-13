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

vAllowedLangs = [ 'arc', 'grc', 'he', 'la' ]

# Loop through the list of texts, parse XML, make data frames, save as CSV
for strTextFullPath in vTextFullPaths:
	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strTextFullPath.split(os.sep)[-1]

	# Current parser options clean up redundant namespace declarations and remove patches of whitespace
	# For more info, see "Parser Options" in: https://lxml.de/parsing.html
	parser = etree.XMLParser(ns_clean=True, remove_blank_text=False)

	try:
		xmlText = etree.parse(strTextFullPath, parser)
	except:
		print(strTextFilename)
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
		# strXMLText = re.sub(r"<supplied(([^>]+|\s)*?)/>", r" ", strXMLText)
		# strXMLText = re.sub(r'<supplied reason="undefined"/>', r" ", strXMLText)

		strXMLText = re.sub(r"(\s+)<supplied>", r"\1<w><supplied>", strXMLText)
		strXMLText = re.sub(r"(\s+)<supplied (([^>]+|\s)*?)>", r"\1<w><supplied \2>", strXMLText)
		strXMLText = re.sub(r"</supplied>(\s+)", r"</supplied></w>\1", strXMLText)
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
		# strXMLText = re.sub(r"<choice>(.*?)</choice>", r"§\1§", strXMLText)
		# strXMLText = re.sub(r"<choice([^>]*?)>(.*?)</choice>", r"§\2§", strXMLText)
		# strXMLText = re.sub(r"<([/]*)choice([/]*)>", "", strXMLText)
		strXMLText = re.sub(r"(\s*)<choice([^>]*?)>", r"<w><choice \1>", strXMLText)
		strXMLText = re.sub(r"</choice>(\s*)", r"</choice></w>", strXMLText)

		strXMLText = re.sub(r"<sic([^>]*?)>(.*?)</sic>", r"", strXMLText)
		strXMLText = re.sub(r"<([/]*)sic([/]*)>", "", strXMLText)
		strXMLText = re.sub(r"<corr([^>]*?)>(.*?)</corr>", r"\2", strXMLText)

		# Orig/Reg
		strXMLText = re.sub(r"<orig([^>]*?)>(.*?)</orig>", r"", strXMLText)
		strXMLText = re.sub(r"<reg([^>]*?)>(.*?)</reg>", r"\2", strXMLText)

		# Deal roughly with word breaks and <foreign ...>
		# Foreign may have one or more words with it
		# strXMLText = re.sub(r"<foreign xml\:lang=\"(\w+)\">", r"<w><foreign xml:lang='\1'>", strXMLText)
		# strXMLText = re.sub(r"<foreign xml\:lang=\"(\w+(?:-\w+))\">", r"<w><foreign xml:lang='\1'>", strXMLText)
		# strXMLText = re.sub(r"<foreign\s*>", r"<w><foreign>", strXMLText)
		# strXMLText = re.sub(r"<foreign>", r"<w><foreign>", strXMLText)
		# strXMLText = re.sub(r"</foreign>", r"</foreign></w>", strXMLText)

		# Deal with word breaks and <num ...>
		# strXMLText = re.sub(r"<num([^>]*?)>", r"<w><num \1>", strXMLText)
		# strXMLText = re.sub(r"</num>", r"</num></w>", strXMLText)

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

		print('########')
		print('########')
		print('########')
		print(strTextFullPath)
		print(strXMLText)
		print('########')
		print('########')
		print('########')

		strXMLText = re.sub(r"§", " ", strXMLText)    # Finally, collapse word breaks
		editionInput = etree.XML(strXMLText, parser)
	except:
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

		# add version to unique/alphabetize on
		wordElemToken = ''.join(wordElem.itertext()).strip()

		if wordElemText and len(wordElemText):
			if wordElem.attrib[XML_NS + 'lang'] in WORD_LISTS:
				if wordElemToken in WORD_LISTS[wordElem.attrib[XML_NS + 'lang']]:
					WORD_LISTS[wordElem.attrib[XML_NS + 'lang']][wordElemToken].append(wordElemText)
				else:
					WORD_LISTS[wordElem.attrib[XML_NS + 'lang']][wordElemToken] = [wordElemText]
			else:
				WORD_LISTS[wordElem.attrib[XML_NS + 'lang']] = {}
				WORD_LISTS[wordElem.attrib[XML_NS + 'lang']][wordElemToken] = [wordElemText]

# Write word lists to CSV files
for lang in WORD_LISTS:

	# Sort alphabetically
	sorted_lang_dict = collections.OrderedDict(sorted(WORD_LISTS[lang].items()))

	# write to file
	with open(strPathListOut + '/word_list_{}.csv'.format(lang), 'w') as csvfile:
		csvwriter = csv.writer(csvfile)
		for word in sorted_lang_dict:
			row = []
			row.append(word)
			row.append(len(sorted_lang_dict[word]))
			row.extend(sorted_lang_dict[word])
			csvwriter.writerow(row)

print(WORD_COUNT)
