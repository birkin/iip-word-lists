import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from gspread_formatting import *

# Bunch of junk for testing

full_list = ["asdf", "asdf"]



# use creds to create a client to interact with the Google Drive API
# scope = ['https://spreadsheets.google.com/feeds']
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
# scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']

strClientSecrets = "iip-wordlist-fb372d3696e5"
creds = ServiceAccountCredentials.from_json_keyfile_name(strClientSecrets+'.json', scope)


client = gspread.authorize(creds)
print(client)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
strSheet = "API Test"
sheet = client.open(strSheet)


# strDate = datetime.today().strftime('%Y-%m-%d')
#
# sheet = client.create('Wordlist')
# sheet.share('christiancasey86@gmail.com', perm_type='user', role='owner')
# sheet.add_worksheet("Latin",1,20)

quit()

vTitles = ["Lemma", "Variation", "File", "Correct?", "Error?", "Correction", "Extra"]
vLanguages = ["Latin", "Greek", "Hebrew", "Aramaic"]
# dLanguages = {'la':'Latin', 'grc'
vWS = {}
for strLanguage in vLanguages:
	try:
		ws = sheet.worksheet(strLanguage)
	except:
		ws = sheet.add_worksheet(strLanguage,1,len(vTitles))
	ws.clear()
	# ws.resize(1)
	ws.insert_row(vTitles,1)
	ws.resize(20)
	vWS.update({strLanguage: ws})

strLanguage = "Latin"

ws = vWS[strLanguage]
ws.resize(2)
print(ws.row_count)

print(ws.get_all_values())

# fmt = cellFormat(
#     backgroundColor=color(1, 0.9, 0.9),
#     textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
#     horizontalAlignment='CENTER',
# 	dataValidationRule='CENTER'
#     )
# format_cell_range(worksheet, 'A1:J1', fmt)