from __future__ import print_function
import httplib2
import os, io

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
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive API Python Quickstart'
        authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
        credentials = authInst.getCredentials()

        #authorize with googleAPI and upload csv as google sheet
        http = credentials.authorize(httplib2.Http())
        drive_service = discovery.build('drive', 'v3', http=http)

        file_metadata = {'name': self.FILENAME, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
        media = MediaFileUpload(self.FILEPATH,
                                mimetype=self.MIMETYPE)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % file.get('id'))