#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run lemmatizer on each text and output data with words tagged.

Created on Mon Jun 10 16:55:01 2019

@author: christiancasey
"""

import os
import glob
import pandas

# Local dependencies
from argument_parser import *
from external_lemmatizer import *




# Create list of language codes
############################################################################### TODO: ADD TAGGERS
vLanguageCodes = ['la', 'grc', 'he', 'arc']

# New columns for the dataframe, which will be saved as the output of this step,
# 	i.e. the POS tagging step
# NB Column names are extremely verbose in order to make the output file easy to read
vNewColumns = ['Lemmatizer Lemma']


# Set the input and output paths
strPathIn = '.' + os.sep + 'Step 2 Output - 3 Input'
strPathOut = '.' + os.sep + 'Step 3 Output - 4 Input'

# Get a list of all texts for processing
# Use command line arguments of the form --texts "file1, file2, file3, etc." when given
# Otherwise, just use all files in the input directory
bClearFolder = False
vFilenames = ParseArguments()
if vFilenames is None:
	vTextFullPaths = glob.glob(strPathIn + os.sep + '*.csv')
	vTextFullPaths.sort()
	bClearFolder = True
else:
	vTextFullPaths = [strPathIn + os.sep + strFilename for strFilename in vFilenames]

#vTextFullPaths = [strPathIn + os.sep + 'aaaa0001.csv']
vTextFullPaths.sort()

# Clear the output folder if no file list given
if bClearFolder:
	vFiles = glob.glob(strPathOut + os.sep + '*')
	for strFile in vFiles:
		os.remove(strFile)


dfAll = None

# Loop through the list of texts and tag parts of speech
for strTextFullPath in vTextFullPaths:
	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strTextFullPath.split(os.sep)[-1]
	
	# Running output, because this one is crazy slow
	print("Processing text: %s" % strTextFilename)
	
	# Load the text data from a csv file
	try:
		dfIn = pandas.read_csv(strTextFullPath)
	except FileNotFoundError:
		print('\n\nText file not found in input data: %s\n\n' % strTextFilename)
		continue

	# Sort the data just in case it is out of order (but it shouldn't be)
	dfIn = dfIn.sort_values(['Text', 'Word Number'])

	# Create copy of input for output variable
	dfOut = dfIn

	# Add new columns to output dataframe
	for strNewColumn in vNewColumns:
		dfOut[strNewColumn] = dfOut.apply(lambda _: '', axis=1)


	# Find out what languages actually appear in this text
	# Then run the POS Tagger on each one
	vLanguagesInText = dfIn['Language'].unique()
	for strLanguage in vLanguagesInText:

		# When the language is not valid, display a warning
		if not strLanguage in vLanguageCodes:
			print("Unsupported or invalid language code: %s" % strLanguage)
			continue

		# Placeholder for processed Lemmatizer output
		# This creates a new dictionary with column names as keys and empty lists as values
		vLemmatizerData = {key: [] for key in vNewColumns}
		
		dfOut = dfOut.sort_values(['Word Number'])
		vWords = dfOut.loc[(dfOut['Language'] == strLanguage)]['Normalized']
		
		for strWord in vWords:
			strLemma = Lemmatize(strWord, strLanguage)
			vLemmatizerData['Lemmatizer Lemma'].append(strLemma)

		# Add the POS Tagger data to the proper columns in the output
		for strNewColumn in vNewColumns:
			dfOut.loc[(dfOut['Language'] == strLanguage), [strNewColumn]] = vLemmatizerData[strNewColumn]

	# Save the results for the current text
	dfOut = dfOut.sort_values(['Word Number'])
	dfOut.to_csv(strPathOut + os.sep + strTextFilename)

	if dfAll is None:
		dfAll = dfOut
	else:
		dfAll = dfAll.append(dfOut)





dfAll.to_csv('Step 3 Output.csv')





