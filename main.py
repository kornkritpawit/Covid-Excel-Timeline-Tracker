from gsheet import gsheetService, pd
from os import listdir, getcwd
from os.path import dirname
from customer import checkCustomerRisk, getTimeline, cleanexcel, getCustomerInfo, isValidTimeline
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(dirname(__file__)+"/.env")
foldername = config.get('EXCEL')

PATH = dirname(__file__) + f'/{foldername}/'
from pprint import pprint
def checkOnefile(file):
    result = []
    excelname = PATH + file
    riskArea = gsheetService()
    customerAllsheet = pd.read_excel(excelname, sheet_name=None).keys()
    customerSheet = [k for k in customerAllsheet if 'Example' not in k]
    customerSheet = [k for k in customerSheet if 'ตัวอย่าง' not in k]
    for j in customerSheet:
        customerData = pd.read_excel(excelname, sheet_name=j)
        customerName = getCustomerInfo(customerData)
        customerData = cleanexcel(customerData)
        customerTimeline = getTimeline(customerData)
        isvalidTl = isValidTimeline(customerTimeline, customerName)
        riskCustomer, riskSheet, risk = checkCustomerRisk(
            customerTimeline, riskArea, customerName)
        # pprint(riskCustomer)
        result.append((file, customerName,isvalidTl, risk, riskCustomer, riskSheet, customerTimeline, customerData.values))
    return result

def checkOneppl(file):
    result = []
    filename = file[:-2]
    sheet = int(file[-1])
    riskArea = gsheetService()
    excelname = PATH + filename
    customerData = pd.read_excel(excelname, sheet_name=sheet)
    customerName = getCustomerInfo(customerData)
    customerData = cleanexcel(customerData)
    customerTimeline = getTimeline(customerData)
    isvalidTl = isValidTimeline(customerTimeline, customerName)
    riskCustomer, riskSheet, risk = checkCustomerRisk(
        customerTimeline, riskArea, customerName)
    result.extend([filename, customerName,isvalidTl, risk, riskCustomer, riskSheet, customerTimeline, customerData.values])
    return result
    # excelname = PATH + 
def checkMany(file):
    finalResult = []
    for i in file:
        finalResult.append(checkOnefile(i))
    return finalResult

