import datetime
from datetime import date
from pythainlp.util.date import thai_full_months
from difflib import get_close_matches
from pprint import pprint

from area import districtEn,districtTh,provinceEn, provinceTh, pd

def getCustomerInfo(data):
    index = 2
    if 'From' in data[data.columns[1]].values:
        index = 3
    
    name = data.columns[index]
    
    if 'บริษัท' in data[data.columns[index]].iloc[0]:
        company = data[data.columns[index]].iloc[0]
    else:
        company = f'บริษัท {data[data.columns[index]].iloc[0]}'    
    return f'{name} {company}'


def cleanexcel(data):
    start_index = None
    data = data.fillna(0)
    if 'From' in data[data.columns[1]].values:
        start_index = data[data[data.columns[1]]=='From'].index[0]
        data = data.drop(data.index[:start_index+1], axis=0)
        data = data.drop(data.columns[1:3], axis=1)
        data = data.drop(data.columns[4:], axis=1)
    else:
        start_index = data[data[data.columns[0]]=='Date'].index[0]
        data = data.drop(data.index[:start_index+1], axis=0)
        data = data.drop(data.columns[1:2], axis=1)
        data = data.drop(data.columns[4:], axis=1)
        
    data.columns = ['วันที่','กิจกรรม/สถานที่','เขต', 'จังหวัด']
    
    data['วันที่'] = data['วันที่'].map(lambda x: dateTransform(x))
    data = cleanDate(data)
    data = cleanMissingDate(data)
    data['วันที่'] = data['วันที่'].map(lambda x: beautyDate(x))
    data = data[data['เขต'] != 0]
    data['จังหวัด'] = data['จังหวัด'].map(lambda x: cleanProvince(x))
    data = cleanDistrict(data)

    return data

def cleanDate(data):
    index = 0
    time_trace = None
    time = None
    day = data['วันที่'].iloc[0]
    for i in data['วันที่']:
        if isinstance(i, pd.Timestamp):
            i = i.to_pydatetime().date()
        if isinstance(i, datetime.date):
            if time_trace == None:
                time_trace = i
            if time_trace > i:  #check if new date is less than current which is wring
                data['วันที่'].iloc[index] = 0
            else:
                time_trace = i
            if day == None:
                day = i
            if day == i and index !=0:
                data['วันที่'].iloc[index] = 0
            elif day !=i and index !=0:
                day = i

        index+=1
    return data

def cleanMissingDate(data):
    day = None
    index = 0
    for i in data['วันที่']:
        if day == None:
            day = i

        if i != day and i !=0:
            day = i
        if i == 0:
            data['วันที่'].iloc[index] = day
        index+=1
    
    return data

def getTimeline(data):
    timeline = {}
    index = 0
    day = None
    place = len(data)
    for i in data['วันที่']:
        day = i
#         if day == None:
#             day = i
        if day not in timeline: #('ket', 'province')
            timeline[day] = {'พื้นที่': set(), 'กิจกรรม': set()}
            timeline[day]['พื้นที่'].add(tuple(data[['เขต', 'จังหวัด']].iloc[index]))
            timeline[day]['กิจกรรม'].add(data['กิจกรรม/สถานที่'].iloc[index])
        elif day in timeline:
            timeline[day]['พื้นที่'].add(tuple(data[['เขต', 'จังหวัด']].iloc[index]))
            timeline[day]['กิจกรรม'].add(data['กิจกรรม/สถานที่'].iloc[index])
        index +=1
    
    return timeline

def dateTransform(x):
    now = datetime.datetime.now()
    currentyear = now.year+543
    if x == 0:
        return x
    elif type(x) == datetime.datetime:
        return x.date()
    else:
        try:
            x = x.split(' ') #['วันจัน' 'month' 'day']
            if len(x)==4:
                x = [i for i in x if 'วัน' not in i]
                if 'คม' in x[1] or 'ยน' in x[1]:
                    monthindex = thai_full_months.index(x[1]) + 1
                    x[1] = monthindex
                else:
                    return 0
            
            elif '/' in x[0] or '-' in x[0]:
                x = x[0]            
            else:
                x = x[-1]            
            if '/' in x:
                x = x.split('/')
            elif '-' in x:
                x = x.split('-')

            if len(x[2]) == 2:
                x[2] = '20'+x[2]

            x = [int(i) for i in x]
            # ควรเปลี่ยนปีเป็น ปัจจุบัน
            if x[2] >= currentyear:
                x[2] -= 543
            day = date(x[2], x[1], x[0])
            return day
        except:
            return 0

def checkInt(i):
    try:
        int(i)
        return True
    except ValueError:
        return False

from langdetect import detect
def checkEng(i):
    try:
        if detect(i) != 'th':
            return True
        else:
            return False
    except Exception as e:
        return True
    

bangkok = ['กทม', 'กรุงเทพ', 'bkk']

def cleanProvince(p):
    if not isinstance(p, str):
        return p
    p = p.lower()
    if len(get_close_matches(p, bangkok)):
        p = 'กรุงเทพ'
    if checkEng(p):
        closest = get_close_matches(p, provinceEn, cutoff=0.3)
    else:
        closest = get_close_matches(p, provinceTh, cutoff=0.3)
    if len(closest):
        p =  closest[0]
        if checkEng(p):
            index = provinceEn.index(p)
            p = provinceTh[index]
        return p
    else:
        return p
    

def cleanDistrict(data):
    index = 0
    for i in data['เขต']:
        district = None
        i = i.strip().lower()
        if checkEng(i):
            if i == 'mueang':
                disEn = i+data['จังหวัด'].iloc[index]
            else:
                disEn = i
            closestEn = get_close_matches(disEn, districtEn, cutoff=0.3)
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
            closestTh = get_close_matches(disTh, districtTh, cutoff=0.3)
            if len(closestTh):
                district = closestTh[0]
                data['เขต'].iloc[index] = district
        index+=1
        
    return data

# from googletrans import Translator

# def translateEngToTh(i):
#     if not checkEng(i):
#         return i

#     translator = Translator()
#     word = i.replace(' ', '')
#     th = translator.translate(word, dest='th')
#     return th.text

def isValidTimeline(tl, name):
    if len(tl) > 10:
        # print(f'{name} write  is valid timeline ({len(tl)} days)')
        return 1
    elif len(tl) == 0:
        return 2
    else:
        # print(f'{name} timeline is invalid ({len(tl)} days)')
        return False

def beautyDate(day):
    try:
        day = day.strftime('%A %d %B %Y')
        return day
    except:
        return day

def checkCustomerRisk(customerTl, riskArea, customername):
    day = None
    riskCustomer = {}
    customerInfo = customerTl.copy()
    riskSheet = {}
    risk = 0
    for i in customerTl:
        area = set()
        for j in customerTl[i]['พื้นที่']:
            if j in riskArea:
                if i not in riskCustomer:
                    riskCustomer[i] = {'พื้นที่': set(), 'กิจกรรม': customerTl[i]['กิจกรรม']}
                    riskCustomer[i]['พื้นที่'].add(j)
                elif i in riskCustomer:
                    riskCustomer[i]['พื้นที่'].add(j)
                riskSheet[j] = riskArea[j]
                risk+=1
    
    for i in riskCustomer:
        riskCustomer[i]['พื้นที่'] = list(riskCustomer[i]['พื้นที่'])
        
#                 print(i, j, customerTl[i]['กิจกรรม'])
                
    # print('---customer enter risk area---')
    # pprint(riskCustomer)
    # print('===Risk area in TrueIdc google sheet===')
    # pprint(riskSheet)
    # print(f'totalrisk = {risk}')

    # if risk:
    #     print(f'{customername} สุ่มเสี่ยง โควิด')
    # else:
    #     print(f'{customername} ปลอดภัย')
    
    return riskCustomer,riskSheet, risk


def checkCustomerRisk2(customerTl, riskArea, customername):
    day = None
    riskCustomer = {}
    customerInfo = customerTl.copy()
    riskSheet = {}
    risk = 0
    for i in customerTl:
        area = set()
        for j in customerTl[i]['พื้นที่']:
            if j in riskArea:
                if i not in riskCustomer:
                    riskCustomer[i] = {'พื้นที่': set(), 'กิจกรรม': customerTl[i]['กิจกรรม']}
                    riskCustomer[i]['พื้นที่'].add(j)
                elif i in riskCustomer:
                    riskCustomer[i]['พื้นที่'].add(j)
                
                riskSheet[j] = riskArea[j]
                
                risk+=1
#                 print(i, j, customerTl[i]['กิจกรรม'])
                
    print('---customer enter risk area---')
    pprint(riskCustomer)
    print('===Risk area in TrueIdc google sheet===')
    pprint(riskSheet)
    print(f'totalrisk = {risk}')
    if risk:
        print(f'{customername} สุ่มเสี่ยง โควิด')
    else:
        print(f'{customername} ปลอดภัย')
    
    return riskCustomer,riskSheet, risk