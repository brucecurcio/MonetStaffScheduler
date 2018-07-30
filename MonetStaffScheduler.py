import json
import csv
import requests
import os
from pprint import pprint
import datetime

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


def slSplit(fullSchedule):


#def qmSplit(fullSchedule):


#def stbSplit(fullSchedule):


#def availableSplit(fullSchedule):


#def buildCSV(slSchedule, qmSchedule, stbSchedule, availableSchedule):


#def sendToGoogle(scheduleCSV):


if __name__ == "__main__":
    bearerToken = getBearerToken() #get bearer token from Monet
    fullSchedule = getSchedule(bearerToken) #grab full schedule from Monet
    slSchedule = slSplit(fullSchedule) #pull out an order ShiftLead schedule
    #qmSchedule = qmSplit(fullSchedule) #pull out and order QM schedule
    #stbSchedule = stbSplit(fullSchedule) #pull out and order TSE3 Standby schedule
    #availableSchedule = availableSplit(fullSchedule) #pull our and order bullpen duties

    #scheduleCSV = buildCSV(slSchedule, qmSchedule, stbSchedule, availableSchedule)
    
    #sendToGoogle(scheduleCSV)