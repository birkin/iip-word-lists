#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEI XML Parser

Parse XML text and create output csv with all data necessary for the word list.

Created on Mon Jun 10 16:55:01 2019

@author: christiancasey
"""

import os
import glob
import pandas
import re
from lxml import etree
from io import StringIO, BytesIO
#import treetaggerwrapper

# Local dependencies
from argument_parser import *


# Set the input and output paths
strPathIn = '.' + os.sep + 'Step 0 Output - 1 Input'
strPathOut = '.' + os.sep + 'Step 1 Output - 2 Input'

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

# Clear the output folder if no file list given
# because this means that this is a full run on all files, not an update
if bClearFolder:
	vFiles = glob.glob(strPathOut + os.sep + '*')
	for strFile in vFiles:
		os.remove(strFile)

#%%

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
	parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
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

	# Get the diplomatic if there is no transcription
	# Don't really do this yet, because the diplomatic can't be processed right now
#	if len(x) < 1:
#		x = xmlText.findall(".//tei:div[@type='edition'][@subtype='diplomatic']/p", namespaces=nsmap)
	
	# Skip it if the text has no textual content,
	if len(x) < 1:
#		print('Error in ' + strTextFilename)
		vFoobarred.append(strTextFilename)
		continue

	# Get script/language from attribute on <p> when it exists
	# Right now this is unused, according to TEI, defines script (which is already obvious)
	if XML_NS + 'lang' in x[0].attrib:
		strPLanguage = x[0].attrib[XML_NS + 'lang']
	
	strXMLText = etree.tostring(x[0], encoding = "unicode")
	

	# The following lines parse the XML to extract the text
	# and format it so that it can be used for later steps.
	# 
	# Word break character: § (alt 6)
	# Line break character: ¶ (alt 7)
	# Alternate character:  ª (alt 9)
	
	# TEMP - Fix mistakes in XML that should be fixed manually	
	strXMLText = re.sub(r"⎜", "|", strXMLText)
	strXMLText = re.sub(r"[\(\)\'‘ʾʹ̒'̔ˊ´’\?\*]", "", strXMLText)
	
	
	# Delete all newlines
	strXMLText = re.sub(r"\n", "", strXMLText)
	
	# Clean up, replace line breaks
	strXMLText = re.sub(r"<p([^>]*)>", "", strXMLText)
	strXMLText = re.sub(r"</p>", "", strXMLText)
	strXMLText = re.sub(r"<lb break=\"no\"(\s*)/>", "¶", strXMLText)
	strXMLText = re.sub(r"\|", "¶", strXMLText)
	strXMLText = re.sub(r"<([/]*)[cl]b(\s*)([/]*)>", "§¶§", strXMLText)
	
	# Just delete <note>...</note> right from the start. Shouldn't be there anyway.
	strXMLText = re.sub(r"<note>([^<]*?)</note>", "", strXMLText)
	
	# Keep stuff as is without worrying about the markup
	strXMLText = re.sub(r"<supplied>(.*?)</supplied>", r"\1", strXMLText)
	strXMLText = re.sub(r"<supplied (([^>]+|\s)*?)>(.*?)</supplied>", r"\3", strXMLText)
	strXMLText = re.sub(r"</supplied>", r"", strXMLText)
	strXMLText = re.sub(r"<unclear([^>]*?)>(.*?)</unclear>", r"\2", strXMLText)
	strXMLText = re.sub(r"<hi ([^>]*?)>(.*?)</hi>", r"\2", strXMLText)
	
	# Discard a bunch of stuff that we don't really care about in this context
	strXMLText = re.sub(r"<([/]*)gap([/]*)>", "", strXMLText)
	strXMLText = re.sub(r"<([/]*)gap ([^>]*?)>", "", strXMLText)
	strXMLText = re.sub(r"<g ([^>]*?)>([^<]*)</g>", "", strXMLText)
	strXMLText = re.sub(r"<g>([^<]*)</g>", "", strXMLText)
	strXMLText = re.sub(r"<g([^>]*?)>", "", strXMLText)
	strXMLText = re.sub(r"<surplus([^>]*?)>(.*?)</surplus>", "", strXMLText)
	strXMLText = re.sub(r"<orgName>(.*?)</orgName>", "", strXMLText)
	strXMLText = re.sub(r"<([/]*)handShift([^>]*?)>", "", strXMLText)
	strXMLText = re.sub(r"<unclear([^>]*?)>", "", strXMLText)
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
	strXMLText = re.sub(r"<foreign xml\:lang=\"(\w+)\">", r"§<foreign_\1>", strXMLText)
	strXMLText = re.sub(r"</foreign>", r"</foreign>§", strXMLText)
	
	# Deal with word breaks and <num ...>
	strXMLText = re.sub(r"<num([^>]*?)>", r"§<num>", strXMLText)
	strXMLText = re.sub(r"</num>", r"</num>§", strXMLText)
	
	# Deal with <expan>
	strXMLText = re.sub(r"<expan>(.*?)</expan>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<expan([^>]*?)>(.*?)</expan>", r"§\2§", strXMLText)
	strXMLText = re.sub(r"<abbr>(.*?)</abbr>", r"§\1", strXMLText)
	strXMLText = re.sub(r"<([/]*)abbr([/]*)>", "", strXMLText)
	
	# Deal with <app>
	strXMLText = re.sub(r"<app>(.*?)</app>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<app([^>]*)>(.*?)</app>", r"\2", strXMLText)
	strXMLText = re.sub(r"<lem>(.*?)</lem>", r"§\1§", strXMLText)
	strXMLText = re.sub(r"<lem ([^>]*?)>(.*?)</lem>", r"§\2§", strXMLText)
	strXMLText = re.sub(r"<rdg>(.*?)</rdg>", r"§ª\1§", strXMLText)
	
	# Normalized
	
	# Expanding abbreviations and such
	strXMLText = re.sub(r"<am>(.*?)</am>", r"", strXMLText)
	strXMLText = re.sub(r"<am/>", r"", strXMLText)
	strXMLText = re.sub(r"<ex>(.*?)</ex>", r"\1§", strXMLText)
	strXMLText = re.sub(r"<ex ([^>]*?)>(.*?)</ex>", r"\2§", strXMLText)
	
	# Replace all spaces as word breaks
	strXMLText = re.sub(r"\s+", "§", strXMLText)
	strXMLText = re.sub(r"[\.\,\:\;‧·⋅•∙]", "§", strXMLText)
	strXMLText = re.sub(r"§\?§", "§", strXMLText)
	
	
	# TEMP ELIMINATE FOREIGN AND NUM
	strXMLText = re.sub(r"<foreign([^>]*?)>(.*?)</foreign>", r"\2", strXMLText)
	strXMLText = re.sub(r"<num([^>]*?)>(.*?)</num>", r"\2", strXMLText)
	strXMLText = re.sub(r"<num>(.*?)</num>", r"\1", strXMLText)
	
	
	# Collapse word breaks and reinstate line breaks
#	strXMLText = re.sub(r"¶", "\n", strXMLText)    # Reinstate line breaks
	strXMLText = re.sub(r"§+", "§", strXMLText)    # Finally, collapse word breaks
	#strXMLText = re.sub(r"§¶§", "§¶", strXMLText)  # Only one word break with line break
	
	# With all tags removed, discard any remaining quotes
	strXMLText = re.sub(r"\"", "", strXMLText)
	
	strExtraCharacters = strExtraCharacters + strXMLText
	
	strTextsAll = strTextsAll + strTextFilename + ":\n" + strXMLText + "\n\n"
	
	
#%%

	iLine = 1
	iWord = 0
	strLang = strMainLanguage
	bNum = 0
	
	vWordsRaw = strXMLText.split('§')
	
	vTextNames = []
	vWords = []
	vWordNum = []
	vStartLines = []
	vEndLines = []
	vNum = []
	vLanguages = []
	vDeleteWord = []
	print(vWordsRaw)
	
	# Pile all of the words into lists
	# Mark certain things for deletion as they're added to be dealt with later
	for strWord in vWordsRaw:
		bDelete = False
		iIncrement = 1  # Increment value is 1 unless the word is marked for deletion or is an alternate
		bNum = 0
		
		# Put the filename in there in the laziest possible way
		vTextNames.append(strTextFilename)
		
		# Add line number, increment using line break symbol
		vStartLines.append(iLine)
		iLineStep = strWord.count('¶')
		iLine += iLineStep
		vEndLines.append(iLine)
		strWord = strWord.replace('¶', '')
		
		# Mark language of word by noting <foreign>
		# TODO: Raise error if more than one <foreign>
		if strWord.count('<foreign') > 0:
			strLang = re.findall(r"<foreign_(\w+)>", strWord)[0]
			strWord = re.sub(r"<foreign_(\w+)>", "", strWord)
			
		vLanguages.append(strLang)
		
		if strWord.count('</foreign') > 0:
			strLang = strMainLanguage
			strWord = re.sub(r"</foreign>", "", strWord)
		
		# Deal with alternates (do not increment word number)
		if strWord.count('ª') > 0:
			iIncrement = 0
			strWord = re.sub(r"ª", "", strWord)
		
		# Deal with numbers
		if strWord.count('<num>') > 0:
			bNum = 1
			strWord = re.sub(r"<num>", "", strWord)
			
		vNum.append(bNum)
		
		if strWord.count('</num>') > 0:
			bNum = 0
			strWord = re.sub(r"</num>", "", strWord)
			
			
		# Append final version of word
		vWords.append(strWord.lower())
		
		# Mark empties for deletion
		if len(strWord.strip()) < 1:
			iIncrement = 0
			bDelete = True
			
		vDeleteWord.append(bDelete)
		
		# Increment the word number, unless it's marked for deletion or an alternate
		iWord += iIncrement
			
		
		vWordNum.append(iWord)
		
		print(strWord)
	#
	#for child in x[0].getchildren():
	#	print(child.tag + "\t" )
	#	
	#	if not child.text is None:
	#		print(child.tag + " text: " + child.text)
	#	if not child.tail is None:
	#		print(child.tag + " tail: " + child.tail)
	
	#%%
	
	data = {'Text': vTextNames,
									'Word Number': vWordNum, 
									'Line Start': vStartLines,
									'Line End': vEndLines,
									'Normalized': vWords,
									'Language': vLanguages,
									'Number': vNum,
									'Delete': vDeleteWord} 
	
	
	dfOut = pandas.DataFrame(data) 
	
	
	dfOut = dfOut.loc[(dfOut['Delete'] == False)]
	dfOut = dfOut.drop(columns=['Delete'])
	
	strOutFileName = re.sub(r"\.xml", ".csv", strTextFilename)
	dfOut.to_csv(strPathOut + os.sep + strOutFileName, index=False)
	
	




################################################################################################
# AFTER LOOP
########################################################################################################
	

strExtraCharacters = re.sub(r"<foreign_([a-z]*)>", "", strExtraCharacters) 	# Tags
#strExtraCharacters = re.sub(r"<([a-z\_/]+)>", "", strExtraCharacters)    	 # Tags
strExtraCharacters = re.sub(r"[0-9]", "", strExtraCharacters)            	 	# Numerals
strExtraCharacters = re.sub(r"[a-zA-Z]", "", strExtraCharacters)           	# Latin
strExtraCharacters = re.sub(r"[\u0370-\u03ff]", "", strExtraCharacters)  	  # Greek
strExtraCharacters = re.sub(r"[\u1f00-\u1ffe]", "", strExtraCharacters)    	# Greek extended
strExtraCharacters = re.sub(r"[\u0590-\u05fe]", "", strExtraCharacters)    	# Hebrew
strExtraCharacters = re.sub(r"[\ufb10-\ufb4f]", "", strExtraCharacters)  	 	# Hebrew
strExtraCharacters = re.sub(r"[§¶ª<>/\-\+]", "", strExtraCharacters)

strExtraCharacters = list(strExtraCharacters)
strExtraCharacters.sort()
strExtraCharacters = list(set(strExtraCharacters))
strExtraCharacters = " ".join(strExtraCharacters)

f = open('All Texts.txt', 'w')
f.write(strTextsAll)
f.close()
f = open('Extra Characters.txt', 'w')
f.write(strExtraCharacters)
f.close()


# WIP Stuff

vFoobarred.sort()
vNoLang.sort()

vLangs = list(set(vLangs))






