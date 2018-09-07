from __future__ import print_function
import httplib2
import os, io
import datetime

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

import auth
class googleapi:

    def __init__(self,FILENAME, FILEPATH, MIMETYPE):
        self.FILENAME = FILENAME
        self.FILEPATH = FILEPATH
        self.MIMETYPE = MIMETYPE
    
    # If modifying these scopes, delete your previously saved credentials
    # at ~/.credentials/drive-python-quickstart.json
    


    def uploadFile(self):

        #get credentials for googleAPI
        SCOPES = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRET_FILE = '/scripts/MonetStaffScheduler/client_secret_IB.json'
        #CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive API Python Quickstart'
        authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
        credentials = authInst.getCredentials()

        #authorize with googleAPI and upload csv as google sheet
        http = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v3', http=http)
        

        file_metadata = {'name': self.FILENAME, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
        media = MediaFileUpload(self.FILEPATH,
                                mimetype=self.MIMETYPE)

        #check list of files in google drive for StaffSchedule; if found, get fileID
        notFound = True
        fileID = drive_service.files().list().execute()

        #array of file id's
        sheetIds = []
        
        #print (fileID)
        for i in range(0, len(fileID['files'])):
            #print (self.FILENAME)
            if self.FILENAME in fileID['files'][i]['name'] + '.csv':
                file = drive_service.files().update(fileId=fileID['files'][i]['id'], body=file_metadata, media_body=media, fields='id').execute()
                notFound = False
                
        
        #if StaffSchedule sheet not found, create a new one
        if notFound == True:
            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            
        
        print('File ID: %s' % file.get('id'))
        print('Sheet updated')
        return (file.get('id'))

    def mergeSheets(self, sheetIds):

        #get credentials for googleAPI
        SCOPES = 'https://www.googleapis.com/auth/drive'
        #CLIENT_SECRET_FILE = '/scripts/MonetStaffScheduler/client_secret_IB.json'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive API Python Quickstart'
        authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
        credentials = authInst.getCredentials()

        #authorize with googleAPI and upload csv as google sheet
        http = credentials.authorize(httplib2.Http())
        sheet_service = discovery.build('sheets', 'v4', http=http)

        # add sheets to spreadsheet
        for i in range(0,7):
            
            #get date to use as sheet names
            sheetDate = datetime.datetime.now() + datetime.timedelta(days=i) # get today's date
            sheetDateString = sheetDate.strftime("%Y-%m-%d") 

            # The ID of the spreadsheet containing the sheet to copy.
            spreadsheet_id = sheetIds[i]  

            #update sheet name of first tab
            if i == 0:
                requestSheetId = sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id)
                sheetResponse = requestSheetId.execute()
                #print ("first sheet renamed")

                # The ID of the sheet.
                sheet_id = sheetResponse['sheets'][0]['properties']['sheetId']

                #rename sheets
                body = {
                    "requests": [{
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": sheet_id,
                                "title": sheetDateString,
                            },
                            "fields": "title",
                        }
                    }]
                }
                sheet_service.spreadsheets().batchUpdate(spreadsheetId=sheetIds[0], body=body).execute()

                #autosize columns to content width
                bodyResize = {
                    "requests": [{
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": 2
                            }
                        }
                    }]
                }
                sheet_service.spreadsheets().batchUpdate(spreadsheetId=sheetIds[0], body=bodyResize).execute() 

            else:
                
                requestSheetId = sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id)
                sheetResponse = requestSheetId.execute()

                # The ID of the sheet to copy.
                sheet_id = sheetResponse['sheets'][0]['properties']['sheetId']

                copy_sheet_to_another_spreadsheet_request_body = {
                    # The ID of the spreadsheet to copy the sheet to.
                    'destination_spreadsheet_id': sheetIds[0],
                }

                request = sheet_service.spreadsheets().sheets().copyTo(spreadsheetId=spreadsheet_id, sheetId=sheet_id, body=copy_sheet_to_another_spreadsheet_request_body)
                response = request.execute()

                new_sheetId = response['sheetId']

                #rename sheets
                body = {
                    "requests": [{
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": new_sheetId,
                                "title": sheetDateString,
                            },
                            "fields": "title",
                        }
                    }]
                }
                sheet_service.spreadsheets().batchUpdate(spreadsheetId=sheetIds[0], body=body).execute()
            
                #autosize columns to content width
                bodyResize = {
                    "requests": [{
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": new_sheetId,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": 2
                            }
                        }
                    }]
                }
                sheet_service.spreadsheets().batchUpdate(spreadsheetId=sheetIds[0], body=bodyResize).execute() 
                
                print(response)      