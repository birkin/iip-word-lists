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
strPathIn = '.' + os.sep + 'Step 3 Output - 4 Input'

# Get a list of all texts for processing
# NB Command line arguments are not used in this step because it must be run on all files
vTextFullPaths = glob.glob(strPathIn + os.sep + '*.csv')
vTextFullPaths.sort()


dfAll = None
print('Loading data files...')

# Loop through the list of texts and tag parts of speech
for strTextFullPath in vTextFullPaths:
	# Extract the filename for the current text
	# Use the OS specific directory separator to split path and take the last element
	strTextFilename = strTextFullPath.split(os.sep)[-1]
	
	# Load the text data from a csv file
	try:
		dfIn = pandas.read_csv(strTextFullPath)
	except FileNotFoundError:
		print('\n\nText file not found in input data: %s\n\n' % strTextFilename)
		continue

	# Sort the data just in case it is out of order (but it shouldn't be)
	dfIn = dfIn.sort_values(['Text', 'Word Number'])

	if dfAll is None:
		dfAll = dfIn
	else:
		dfAll = dfAll.append(dfIn)


print('Loading data files complete.')

#%% Remove duplicates, which is equivalent to uniquing on specific columns

print(dfAll.shape[0])

dfOut = dfAll.drop_duplicates(subset={'Part of Speech', 'Part of Speech (Secondary Info)', 'POS Tagger Lemma', 'Lemmatizer Lemma'}, keep='first')

print(dfOut.shape[0])

dfOut.to_csv('Step 4 Output.csv')





