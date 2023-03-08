from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os
import shutil
from pathlib import Path

def Gdrive_upload(pathScan, filename_log, KeyPath):

  # Below code does the authentication
  # part of the code
  GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = KeyPath + '/client_secrets.json'
  gauth = GoogleAuth()
  # Loads credentials file to handle authentication
  # avoiding need for local webserver
  gauth.LoadCredentialsFile(KeyPath + '/credentials.txt')	
  drive = GoogleDrive(gauth)

  shutil.make_archive(pathScan, 'zip', pathScan)
  upload_file_list = [filename_log, pathScan + '.zip']

  for upload_file in upload_file_list:
    gfile = drive.CreateFile({'title':os.path.basename(upload_file) ,'parents': [{'id': '1YRKbUVB-c9blIZtu_r9LSwjbtfzINMfU'}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(upload_file)
    gfile.Upload(param={'supportsTeamDrives': True}) # Upload the file.
    gfile = None
