from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SAMPLE_SPREADSHEET_ID = '405298722'



# use creds to create a client to interact with the Google Drive API
# scope = ['https://spreadsheets.google.com/feeds']
SCOPES = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
# scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']

strClientSecrets = "iip-wordlist-fb372d3696e5"
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
	with open('token.pickle', 'rb') as token:
		creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
	if creds and creds.expired and creds.refresh_token:
		creds.refresh(Request())
	else:
		flow = InstalledAppFlow.from_client_secrets_file(strClientSecrets+'.json', SCOPES)
		creds = flow.run_local_server()

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range=SAMPLE_RANGE_NAME).execute()
values = result.get('values', [])
# creds = ServiceAccountCredentials.from_json_keyfile_name(, scope)

#
# client = gspread.authorize(creds)
# print(client)
#
# # Find a workbook by name and open the first sheet
# # Make sure you use the right name here.
# strSheet = "API Test"
# sheet = client.open(strSheet)
#
#
# strDateTime = datetime.today().strftime('%Y-%m-%d')
#
# vTitles = ["Lemma", "Variation", "File", "Correct?", "Error?", "Correction", "Extra"]
# vLanguages = ["Latin", "Greek", "Hebrew", "Aramaic"]
#
# vWS = {}
# for strLanguage in vLanguages:
# 	try:
# 		ws = sheet.worksheet(strLanguage)
# 	except:
# 		ws = sheet.add_worksheet(strLanguage,1,len(vTitles))
# 	ws.clear()
# 	# ws.resize(1)
# 	ws.insert_row(vTitles,1)
# 	# ws.resize(2)
# 	vWS.update({strLanguage: ws})
#
# strLanguage = "Latin"
#
# ws = vWS[strLanguage]
# ws.resize(2)
# print(ws.row_count)
#
# print(ws.get_all_values())
#
# # fmt = cellFormat(
# #     backgroundColor=color(1, 0.9, 0.9),
# #     textFormat=textFormat(bold=True, foregroundColor=color(1, 0, 1)),
# #     horizontalAlignment='CENTER',
# # 	dataValidationRule='CENTER'
# #     )
# # format_cell_range(worksheet, 'A1:J1', fmt)