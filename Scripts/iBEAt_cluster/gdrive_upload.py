from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import os
import shutil
from pathlib import Path

def Gdrive_upload(pathScan, filename_log):

  # Below code does the authentication
  # part of the code
  gauth = GoogleAuth()
  # Creates local webserver and auto
  # handles authentication.
  gauth.LocalWebserverAuth()	
  drive = GoogleDrive(gauth)

  shutil.make_archive(pathScan, 'zip', pathScan)
  upload_file_list = [filename_log, pathScan + '.zip']

  for upload_file in upload_file_list:
    gfile = drive.CreateFile({'title':os.path.basename(upload_file) ,'parents': [{'id': '1CMQKXKcVxX_62Ms8rX5cJEMnrMPClm_B'}]})
    # Read file and set it as the content of this instance.
    gfile.SetContentFile(upload_file)
    gfile.Upload(param={'supportsTeamDrives': True}) # Upload the file.
    gfile = None
