import json
import csv
import requests
import os
from pprint import pprint
import datetime
from operator import itemgetter

def getBearerToken():
    
    #read username from txt file
    with open("basicAuth.txt", "r") as basicAuth:
        basicAuthString = basicAuth.read()

    #headers for api call to monet
    headers = {"Accept": "application/x-www-form-urlencoded",
               "Authorization": "Basic " + basicAuthString}

    #get bearer token from Monet
    try:
        bearerToken = requests.post('https://api.wfmlive.com/Authentication', headers=headers, data='Tenant=Infoblox')
    except ValueError:
            print('there was a problem getting the bearer token')

    tokenString = bearerToken.text #convert json to string
    tokenDict = json.loads(tokenString) #convert string to dict
    
    return tokenDict['token'] #return just bearer token string


def getSchedule(bearerToken):
    #headers for api call to monet
    headers = {"Accept": "application/json",
               "Authorization": "Bearer " + bearerToken}
    
    #get today and tomorrow's date
    now = datetime.datetime.now() # get today's date
    tomorrow = now + datetime.timedelta(days=1) #get tomorrow's date
    
    #reformat dates for Monet call
    nowFormat = now.strftime("%Y-%m-%d")
    tomorrowFormat = tomorrow.strftime("%Y-%m-%d")

    #get Full Schedule from Monet
    try:
        fullSchedule = requests.get('https://api.wfmlive.com/Workhours?fromDate=' + nowFormat + '&toDate=' + tomorrowFormat + '&mode=detailed&agentId=all&workgroupname=all', headers=headers)
    except ValueError:
            print('there was a problem getting the Full Monet Schedule')
    
    scheduleString = fullSchedule.text #convert json to string
    scheduleDict = json.loads(scheduleString) #convert string to dict
    
    return (scheduleDict)


def slSplit(fullScheduleDict):

    slSchedule = [] #initialize empty list

    #pull out shift lead assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'SHIFT LEAD' in fullSchedule['Result'][i]['workDescription']:
            slSchedule.append(fullSchedule['Result'][i])

    #reorder shift lead assignments chronologically
    orderedSLSchedule = sorted(slSchedule, key=itemgetter('startUTC'))
    #print(orderedSLSchedule)

    return(orderedSLSchedule)   


def qmSplit(fullSchedule):
    qMSchedule = [] #initialize empty list

    #pull out QM assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Queue Monitor' in fullSchedule['Result'][i]['workDescription']:
            qMSchedule.append(fullSchedule['Result'][i])
        
    #reorder QM assignments chronologically
    orderedQMSchedule = sorted(qMSchedule, key=itemgetter('startUTC'))
    #print(orderedQMSchedule)

    return(orderedQMSchedule)

def stbSplit(fullSchedule):
    stbSchedule = [] #initialize empty list

    #pull out STB assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Stand-By' in fullSchedule['Result'][i]['workDescription']:
            stbSchedule.append(fullSchedule['Result'][i])
        
    #reorder STB assignments chronologically
    orderedSTBSchedule = sorted(stbSchedule, key=itemgetter('startUTC'))
    #print(orderedSTBSchedule)

    return(orderedSTBSchedule)


def availableSplit(fullSchedule):
    availableSchedule = [] #initialize empty list

    #pull out Available assignments from full schedule
    for i in range(0, len(fullSchedule['Result'])):
        if 'Available' in fullSchedule['Result'][i]['workDescription']:
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
                
    return(theSchedule)
        


def buildCSV(slSchedule, qmSchedule, stbSchedule, availableSchedule):
    with open('StaffSchedule.csv', 'w', newline='') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, slSchedule[0].keys())

        w.writerow({'employeeFullName': 'SHIFTLEAD', 'startUTC':'','endUTC':''})
        w.writeheader()
        w.writerows(slSchedule)
        
        w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
        w.writerow({'employeeFullName': 'QM', 'startUTC':'','endUTC':''}) #write role to row
        w.writeheader()
        w.writerows(qmSchedule)
        
        w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
        w.writerow({'employeeFullName': 'STANDBY', 'startUTC':'','endUTC':''}) #write role to row
        w.writeheader()
        w.writerows(stbSchedule)

        w.writerow({'employeeFullName': '', 'startUTC':'','endUTC':''}) #empty row spacer
        w.writerow({'employeeFullName': 'Available', 'startUTC':'','endUTC':''}) #write role to row
        w.writeheader()
        w.writerows(availableSchedule)


#def sendToGoogle(scheduleCSV):


if __name__ == "__main__":
    bearerToken = getBearerToken() #get bearer token from Monet
    fullSchedule = getSchedule(bearerToken) #grab full schedule from Monet
    
    #extract schedule and reorder entries according to start time
    slSchedule = slSplit(fullSchedule) 
    qmSchedule = qmSplit(fullSchedule) 
    stbSchedule = stbSplit(fullSchedule) 
    availableSchedule = availableSplit(fullSchedule)

    #remove unneeded columns from schedule
    slScheduleFiltered = removeFields(slSchedule)
    qmScheduleFiltered = removeFields(qmSchedule)
    stbScheduleFiltered = removeFields(stbSchedule)
    availableScheduleFiltered = removeFields(availableSchedule)

    #adjust timezone to PST/PDT and strip month/day/year from time - TBD
    

    scheduleCSV = buildCSV(slScheduleFiltered, qmScheduleFiltered, stbScheduleFiltered, availableScheduleFiltered)
    
    #sendToGoogle(scheduleCSV)