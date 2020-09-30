mport csv
import os
import requests
from iip_smr_web_app import settings_app
import xml.etree.ElementTree as ET

LATIN_TEXT = 0
LATIN_WORDNUM = 1
LATIN_WORD = 7
LATIN_POS1 = 8
LATIN_POS2 = 9
LATIN_LEMMA = 10
XML1 = 11
XML2 = 12
NEWBUFF = 3

KWIC_BUFF = 2

with open('latin_doubletree_data.txt', 'w') as f:
	sys.stdout = f
	with requests.Session() as s:
		download = s.get("https://raw.githubusercontent.com/Brown-University-Library/iip-word-lists/master/new%20version%20test/Step%204%20New%20Output.csv")
		decoded = download.content.decode('utf-8')
		csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
		line_count = 0
		curtext = ""
		textrows = []
		for row in csv_reader:
			row_word = row[LATIN_LEMMA + NEWBUFF]
			if line_count > 0 and len(row_word) > 0 and row_word[:1] != "?":
				if curtext != row[LATIN_TEXT + NEWBUFF]:
					go_through_text(textrows, words)
					curtext = row[LATIN_TEXT + NEWBUFF]
					textrows = []
				else:
					textrows.append(row)
			line_count += 1
		go_through_text(textrows)


def go_through_text(textrows):
	











