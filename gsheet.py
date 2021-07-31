from __future__ import print_function
import os.path
from os.path import *

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import pandas as pd
import numpy as np

from customer import *
from area import *
from difflib import *

PATH = dirname(__file__) + '/'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1prrglTLAxwvUtQ7ciztKQWpvYpPEOibWFstrlvA518Y'
SAMPLE_RANGE_NAME = 'แผ่น1!B1:E'

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        print(creds.valid, creds.expired)
        print(creds.refresh_token)
        try:
            creds.refresh(Request())
        except Exception as e:
            print(e)
            flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

from datetime import datetime

def cleanGsheet(data):
    raw = []
    for i in data:
        if i == []:
            break
        raw.append(i)
    dataNp = np.array(raw)
    dataDf = pd.DataFrame(dataNp[1:], columns=dataNp[0])
    dataDf.columns = ['กลุ่มคลัสเตอร์','พื้นที่เสี่ยง', 'จังหวัด', 'วันที่ปลดล็อค']
    dataDf['วันที่ปลดล็อค'] = dataDf['วันที่ปลดล็อค'].map(lambda x: dateTransform(x))
    dataDf = dataDf[dataDf['วันที่ปลดล็อค'] > datetime.now().date()]
    dataDf = cleanDistrictGsheet(dataDf)
    dataDf['จังหวัด'] = dataDf['จังหวัด'].map(lambda x: cleanProvince(x))
    return dataDf

def cleanDistrictGsheet(data):
    index = 0
    for i in data['พื้นที่เสี่ยง']:
        district = None
        i = i.strip().lower()
        if checkEng(i):
            if i == 'mueang':
                disEn = i+data['จังหวัด'].iloc[index]
            else:
                disEn = i
            closestEn = get_close_matches(disEn, districtEn, cutoff=0.4)
            if len(closestEn):
                closestEn = closestEn[0]
                idist = districtEn.index(closestEn)
                district = districtTh[idist]
                data['เขต'].iloc[index] = district

        else:
            if 'อ.เมือง' in i or 'อำเภอเมือง' in i or 'เมือง' == i:
                disTh = 'เมือง' + data['จังหวัด'].iloc[index]
            else:
                disTh = i
            closestTh = get_close_matches(disTh, districtTh, cutoff=0.4)
            if len(closestTh):
                district = closestTh[0]
                data['พื้นที่เสี่ยง'].iloc[index] = district
        index+=1
        
    return data

def getRiskArea(data):
    area = {}
    index = 0
#     dataIndex =
    total = len(data)
    for i in data[['พื้นที่เสี่ยง', 'จังหวัด']].values:
        cluster = []
        areaKey = None
        current = tuple(i)
        if current not in area:
            area[current] = [tuple(data[['กลุ่มคลัสเตอร์', 'วันที่ปลดล็อค']].iloc[index])]

        elif current in area:
#             print('else',index, i)
            area[current].append(tuple(data[['กลุ่มคลัสเตอร์', 'วันที่ปลดล็อค']].iloc[index]))
        index+=1
    return area


def gsheetService():
    service = build('sheets', 'v4', credentials=creds)
    sheet_service = service.spreadsheets()
    result = sheet_service.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()

    riskAreaRaw = result.get('values', [])
    riskAreaDf = cleanGsheet(riskAreaRaw)
    riskArea = getRiskArea(riskAreaDf)
    return riskArea



