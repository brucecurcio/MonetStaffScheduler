import json
import csv
import requests
import os
from pprint import pprint
import datetime
from operator import itemgetter
import time

import googleAPI

def getBearerToken():
    
    #read username from text file
    with open("/scripts/MonetStaffScheduler/basicAuth.txt", "r") as basicAuth:
    #with open("./basicAuth.txt", "r") as basicAuth:
        basicAuthString = basicAuth.read()

    #headers for api call to monet
    headers = {"Accept": "application/x-www-form-urlencoded", "Authorization": "Basic " + basicAuthString.rstrip("\n")}
 
    #get bearer token from Monet
    try:
        bearerToken = requests.post('https://api.wfmlive.com/Authentication', headers=headers, data='Tenant=Infoblox')
    except ValueError:
        print('there was a problem getting the bearer token')

    tokenString = bearerToken.text #convert json to string
    tokenDict = json.loads(tokenString) #convert string to dict
    
    return tokenDict['token'] #return just bearer token string


def getSchedule(bearerToken, i):
    #headers for api call to monet
    headers = {"Accept": "application/json",
               "Authorization": "Bearer " + bearerToken}
    
    #get today and tomorrow's date
    #now = datetime.datetime.now() + datetime.timedelta(days=-1) # get monday for developing on weekend
    #tomorrow = now + datetime.timedelta(days=1) #get tuesday for developing on weekend
    
    now = datetime.datetime.now() + datetime.timedelta(days=i)# get today's date
    tomorrow = now + datetime.timedelta(days=1) #get tomorrow's date
    
    #check for daylight savings time and reformat dates for Monet Call (PDT = -7, PST = -6)
    theTime = time.localtime()
    if theTime.tm_isdst == 0:
        nowFormat = now.strftime("%Y-%m-%d")+'T08:00:00'
        tomorrowFormat = tomorrow.strftime("%Y-%m-%d")+'T07:59:59'
        print ('pst')
    else:
        nowFormat = now.strftime("%Y-%m-%d")+'T07:00:00'
        tomorrowFormat = tomorrow.strftime("%Y-%m-%d")+'T06:59:59'
        print ('pdt')

    #get Full Schedule from Monet
    try:
        fullSchedule = requests.get('https://api.wfmlive.com/Workhours?fromDate=' + nowFormat + '&toDate=' + tomorrowFormat + '&mode=detailed&agentId=all&workgroupname=all', headers=headers)
    except ValueError:
            print('there was a problem getting the Full Monet Schedule')
    
    #print(fullSchedule.text)
    scheduleString = fullSchedule.text #convert json to string
    scheduleDict = json.loads(scheduleString) #convert string to dict
    
    return (scheduleDict)


def slSplit(fullScheduleDict):

    slSchedule = [] #initialize empty list
    #print(fullScheduleDict)
    #pull out shift lead assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'SHIFT LEAD' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' not in fullSchedule['Result'][i]['externalID']:
            #print(fullSchedule['Result'][i]['workDescription']+fullSchedule['Result'][i]['employeeFullName']+' SL')
            slSchedule.append(fullSchedule['Result'][i])
        elif 'Dual Role' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' not in fullSchedule['Result'][i]['externalID']:
            #print(fullSchedule['Result'][i]['workDescription']+fullSchedule['Result'][i]['employeeFullName']+' DUAL')
            slSchedule.append(fullSchedule['Result'][i])

    #reorder shift lead assignments chronologically
    orderedSLSchedule = sorted(slSchedule, key=itemgetter('startUTC'))

    #print(orderedSLSchedule)
    return(orderedSLSchedule)   

def slSplitNMRI(fullScheduleDict):

    slScheduleNMRI = [] #initialize empty list

    #pull out shift lead assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'SHIFT LEAD' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' in fullSchedule['Result'][i]['externalID']:
            slScheduleNMRI.append(fullSchedule['Result'][i])

    #reorder shift lead assignments chronologically
    orderedSLScheduleNMRI = sorted(slScheduleNMRI, key=itemgetter('startUTC'))
    
    #print(orderedSLScheduleNMRI)
    return(orderedSLScheduleNMRI)


def qmSplit(fullSchedule):
    qMSchedule = [] #initialize empty list

    #pull out QM assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Queue Monitor' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' not in fullSchedule['Result'][i]['externalID']:
            qMSchedule.append(fullSchedule['Result'][i])
        elif 'Dual Role' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' not in fullSchedule['Result'][i]['externalID']:
            qMSchedule.append(fullSchedule['Result'][i])
        
    #reorder QM assignments chronologically
    orderedQMSchedule = sorted(qMSchedule, key=itemgetter('startUTC'))
    #print(orderedQMSchedule)

    return(orderedQMSchedule)

def qmSplitNMRI(fullSchedule):
    qMScheduleNMRI = [] #initialize empty list

    #pull out QM assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Queue Monitor' in fullSchedule['Result'][i]['workDescription'] and 'NMRI' in fullSchedule['Result'][i]['externalID']:
            qMScheduleNMRI.append(fullSchedule['Result'][i])
        
    #reorder QM assignments chronologically
    orderedQMScheduleNMRI = sorted(qMScheduleNMRI, key=itemgetter('startUTC'))
    
    #print(orderedQMScheduleNMRI)
    return(orderedQMScheduleNMRI)

def stbSplit(fullSchedule):
    stbSchedule = [] #initialize empty list

    #pull out STB assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Stand-By' in fullSchedule['Result'][i]['workDescription'] and 'TSE1' not in fullSchedule['Result'][i]['externalID']:
            stbSchedule.append(fullSchedule['Result'][i])
        
    #reorder STB assignments chronologically
    orderedSTBSchedule = sorted(stbSchedule, key=itemgetter('startUTC'))
    #print(orderedSTBSchedule)

    return(orderedSTBSchedule)


def stbSplitTSE1(fullSchedule):
    stbScheduleTSE1 = [] #initialize empty list
    
    #pull out STB assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Stand-By' in fullSchedule['Result'][i]['workDescription'] and 'TSE1' in fullSchedule['Result'][i]['externalID']:
            stbScheduleTSE1.append(fullSchedule['Result'][i])
        
    #reorder STB assignments chronologically
    orderedSTBScheduleTSE1 = sorted(stbScheduleTSE1, key=itemgetter('startUTC'))
    
    #print(orderedSTBScheduleNMRI)
    return(orderedSTBScheduleTSE1)


def availableSplit(fullSchedule):
    availableSchedule = [] #initialize empty list

    #pull out Available assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Available' in fullSchedule['Result'][i]['workDescription'] and 'TSE2' in fullSchedule['Result'][i]['externalID']:
            availableSchedule.append(fullSchedule['Result'][i])
        
    #reorder Available assignments chronologically
    orderedAvailableSchedule = sorted(availableSchedule, key=itemgetter('startUTC'))
    #print(orderedAvailableSchedule)

    return(orderedAvailableSchedule)


def removeFields(theSchedule):
    
    #remove unneeded fields in schedule
    fields = ('agentID','externalID','workgroupName','workDescription','exportCode','user1',
       'user2','user3','utcOffset','totalDuration','personalDuration')
    
    for i in range(0, len(theSchedule)):
        for key in fields:
            if key in theSchedule[i]:
                del theSchedule[i][key]
    #print (theSchedule)            
    return(theSchedule)
        
def timeZoneEdit(Schedule):

    theTime = time.localtime()
    if theTime.tm_isdst == 0:
        delta = -8
    else:
        delta = -7
    
    #pull out assignments from full schedule
    for i in range(0, len(Schedule)):
        
        #adjust start times
        startTimeString = (Schedule[i]['startUTC'])
        try:
            start_time_obj = datetime.datetime.strptime(startTimeString, '%Y-%m-%dT%H:%M:%S') # convert str to datetime obj
            start_time_obj = start_time_obj + datetime.timedelta(hours=delta)
            Schedule[i]['startUTC'] = start_time_obj.strftime("%H:%M:%S") #shave date off, leave time
        except ValueError:
            print(Schedule[i]['employeeFullName'] + ' edit already done ' + str(i))
        
        #adjust end times
        endTimeString = (Schedule[i]['endUTC'])
        try:
            end_time_obj = datetime.datetime.strptime(endTimeString, '%Y-%m-%dT%H:%M:%S') # convert str to datetime obj
            end_time_obj = end_time_obj + datetime.timedelta(hours=delta)
            Schedule[i]['endUTC'] = end_time_obj.strftime("%H:%M:%S") #shave date off, leave time
        except ValueError:
            print(Schedule[i]['employeeFullName'] +' edit already done')
    #print(Schedule)
    return(Schedule)   
  
def buildCSV(slSchedule, qmSchedule, stbSchedule, availableSchedule, slScheduleNMRI, qmScheduleNMRI, stbScheduleTSE1, i):

    #get current date and time for csv header
    current = datetime.datetime.now() # get today's date
    currentFormat = current.strftime("%Y-%m-%d %H:%M")    
        

    if not slSchedule: #check to make sure sl/qm/stb schedule has data 
        with open('StaffSchedule' + str(i) + '.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
            writer = csv.writer(f, delimiter=',')
            if i == 0:
                writer.writerow([currentFormat,''])
            writer.writerow(['No SL/QM/STB schedule published',''])
        
   
    else: #build the CSV
        with open('StaffSchedule' + str(i) + '.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
            fieldnames = ['employeeFullName', 'startUTC', 'endUTC'] # hardcode fieldname column order
            w = csv.DictWriter(f, fieldnames=fieldnames)
                    
            #write DDI TSE2 SL schedule
            if i == 0:
                w.writerow({'employeeFullName': currentFormat, 'startUTC':'','endUTC':''}) #creation date/time
            else:
                w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'SHIFTLEAD-DDI-TSE2', 'startUTC':'START','endUTC':'END'})
            w.writerows(slSchedule)
            
            #write DDI TSE2 QM schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'QM-DDI-TSE2', 'startUTC':'START','endUTC':'END'}) #write role to row
            w.writerows(qmSchedule)
            
            #write DDI TSE2 BP schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'BP-DDI-TSE2 **BETA**', 'startUTC':'START','endUTC':'END'}) #write role to row
            w.writerows(availableSchedule)

            #write DDI TSE3 standby schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'STANDBY-DDI-TSE3', 'startUTC':'START','endUTC':'END'}) #write role to row
            w.writerows(stbSchedule)

            #write TSE1 DDI Standby Schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'STANDBY-DDI-TSE1', 'startUTC':'START','endUTC':'END'}) #write role to row
            w.writerows(stbScheduleTSE1)

            #write NMRI SL schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'SHIFTLEAD-NMRI', 'startUTC':'START','endUTC':'END'})
            w.writerows(slScheduleNMRI)
            
            #write NMRI QM schedule
            w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
            w.writerow({'employeeFullName': 'QM-NMRI', 'startUTC':'START','endUTC':'END'}) #write role to row
            w.writerows(qmScheduleNMRI)
            
if __name__ == "__main__":
    bearerToken = getBearerToken() #get bearer token from Monet
    
    for i in range(0,7):
        fullSchedule = getSchedule(bearerToken, i) #grab full schedule from Monet
        #print(fullSchedule)
        #extract schedule and reorder entries according to start time
        slSchedule = slSplit(fullSchedule) 
        qmSchedule = qmSplit(fullSchedule) 
        stbSchedule = stbSplit(fullSchedule) 
        slScheduleNMRI = slSplitNMRI(fullSchedule)
        qmScheduleNMRI = qmSplitNMRI(fullSchedule)
        stbScheduleTSE1 = stbSplitTSE1(fullSchedule)
        availableSchedule = availableSplit(fullSchedule)

        #remove unneeded columns from schedule
        slScheduleFiltered = removeFields(slSchedule)
        qmScheduleFiltered = removeFields(qmSchedule)
        stbScheduleFiltered = removeFields(stbSchedule)
        slScheduleFilteredNMRI = removeFields(slScheduleNMRI)
        qmScheduleFilteredNMRI = removeFields(qmScheduleNMRI)
        stbScheduleFilteredTSE1 = removeFields(stbScheduleTSE1)
        availableScheduleFiltered = removeFields(availableSchedule)

        #adjust timezone to PST/PDT and strip month/day/year from time - TBD
        sl = timeZoneEdit(slScheduleFiltered)
        qm = timeZoneEdit(qmScheduleFiltered)
        stb = timeZoneEdit(stbScheduleFiltered)
        slNMRI = timeZoneEdit(slScheduleFilteredNMRI)
        qmNMRI = timeZoneEdit(qmScheduleFilteredNMRI)
        stbTSE1 = timeZoneEdit(stbScheduleFilteredTSE1)
        available = timeZoneEdit(availableScheduleFiltered)

        #build the StaffSchedule csv
        buildCSV(sl, qm, stb, available, slNMRI, qmNMRI, stbTSE1, i)
    
    #google sheetID array
    sheetIds = []

    #send csvs to google Sheet
    for i in range(0,7):
        FILENAME = 'StaffSchedule' + str(i) + '.csv'
        FILEPATH = 'StaffSchedule' + str(i) + '.csv'
        MIMETYPE = 'text/csv'

        googleapiInst = googleAPI.googleapi(FILENAME, FILEPATH,  MIMETYPE)
        sheetIds.append(googleapiInst.uploadFile())

    #print(sheetIds)
    googleapiInst = googleAPI.googleapi('none', 'none', 'none')
    googleapiInst.mergeSheets(sheetIds)