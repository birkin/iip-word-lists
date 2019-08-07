import pickle
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scope = ['https://spreadsheets.google.com/feeds',
		 'https://www.googleapis.com/auth/drive']


strClientSecrets = "iip-wordlist-fb372d3696e5"
creds = ServiceAccountCredentials.from_json_keyfile_name("../src/python/"+strClientSecrets+'.json', scope)

client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
strSheet = "API Test"
sheet = client.open(strSheet)

vTitles = ["Lemma", "Variation", "File", "Correct?", "Error?", "Correction", "Extra"]
dLanguages = {'lat':'Latin', 'grc':'Greek', 'heb':'Hebrew', 'arc':'Aramaic'}


# for strKey in dLanguages:

# strLanguage = dLanguages[strKey]
strLanguage = 'Latin'

try:
	ws = sheet.worksheet(strLanguage)
except:
	print('Error opening sheet')
	quit()
# 	ws = sheet.add_worksheet(strLanguage,1,len(vTitles))
# ws.clear()
# ws.insert_row(vTitles,1)
mWS = ws.get_all_values()
nRows = len(mWS)
# nRows = round(len(vWorksheets[strLanguage])/3)  # 3 columns, need # rows
print(len(mWS))
# ws.resize(nRows+1)


vAll = ws.row_values(1)
print(vAll)

val = ws.acell('A2').value
print(val)

val = ws.cell(2, 4).value
print(val)

mWS = ws.get_all_values()
vCorrect = []
for i in len(mWS):
	row = mWS[i]
	if row[3] == 'TRUE':
		vCorrect.append(row[0])

with open('correct.pickle', 'wb') as f:
	pickle.dump(vCorrect, f)

# # print(list_of_lists)
# cell_list = ws.range('A1:G'+str(nRows))

for i in range(nRows):
	if cell_list[i*7+3].value == 'TRUE':
		vCorrect.append(cell_list[i*7+0].value)

with open('correct.pickle', 'wb') as f:
	pickle.dump(vCorrect, f)

# i = 0
# for cell in cell_list:
# 	cell.value = mWS[i]
# 	i+=1

ws.update_cells(cell_list)


with open('correct.pickle', 'rb') as f:
	vCorrect = pickle.load(f)

for x in vCorrectNew:
	print(x)