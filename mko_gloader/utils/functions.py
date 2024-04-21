# import pickle
# import os.path
from pathlib import Path


# # Import google API libraries
# from googleapiclient.http import MediaFileUpload
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import googleapiclient.errors
# from google.oauth2 import service_account
#
# # Import general libraries
# from argparse import ArgumentParser
# from os import chdir, stat
# from sys import exit
# from datetime import datetime
# import ast
# import magic
# import hashlib
#
# # Global list to store file information for upload
# upload_list = []
#
# # If modifying these scopes, delete the file token.pickle.
# SCOPES = ['https://www.googleapis.com/auth/drive']
#
def pathstr_to_list(pathstr: str):
    path = Path(pathstr.strip("\\/"))
    return path.parts
#
#
#
# def logging(log, level=0):
#     curr_time = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
#     if level == 0:
#         print(curr_time + "[INFO] " + log)
#     elif level == 1:
#         print(curr_time + "[WARN] " + log)
#     elif level == 2:
#         print(curr_time + "[CRIT] " + log)
#
#
# def token_auth():
#     """
#                 Authenticate to Google API
#         """
#
#     creds = None
#
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             check_path('../credentials.json')
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 '../credentials.json', SCOPES)
#             # EDIT below to change authentication method,
#             # I prefer run on Console because I'm using linux server without UI
#             creds = flow.run_local_server(port=0)
#             # creds = flow.run_console()
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#
#     return creds
#
#
# def human_bytes(size):
#     """Return the given bytes as a human friendly KB, MB, GB, or TB string"""
#     size = float(size)
#     k_bytes = float(1024)
#     m_bytes = float(k_bytes ** 2)  # 1,048,576
#     g_bytes = float(k_bytes ** 3)  # 1,073,741,824
#     t_bytes = float(k_bytes ** 4)  # 1,099,511,627,776
#
#     if size < k_bytes:
#         return '{0} {1}'.format(size, 'Bytes' if 0 == size > 1 else 'Byte')
#     elif k_bytes <= size < m_bytes:
#         return '{0:.2f} KB'.format(size / k_bytes)
#     elif m_bytes <= size < g_bytes:
#         return '{0:.2f} MB'.format(size / m_bytes)
#     elif g_bytes <= size < t_bytes:
#         return '{0:.2f} GB'.format(size / g_bytes)
#     elif t_bytes <= size:
#         return '{0:.2f} TB'.format(size / t_bytes)
#
#
# def convert_size_to_bytes(size_str):
#     # Split the string into parts (e.g., "0.0" and "Byte")
#     parts = size_str.split()
#
#     # Check if the parts contain a valid number and unit
#     if len(parts) != 2 or not parts[0].replace('.', '', 1).isdigit():
#         raise ValueError("Invalid file size format")
#
#     # Extract the numerical part and convert it to a float
#     size_num = float(parts[0])
#
#     # Define a dictionary to map units to bytes
#     size_units = {
#         "Byte": 1,
#         "KB": 1024,
#         "MB": 1024 ** 2,
#         "GB": 1024 ** 3,
#         "TB": 1024 ** 4,
#         "PB": 1024 ** 5,
#         "EB": 1024 ** 6,
#         "ZB": 1024 ** 7,
#         "YB": 1024 ** 8
#     }
#
#     # Get the unit and convert the size to bytes
#     size_unit = parts[1]
#     if size_unit in size_units:
#         size_in_bytes = int(size_num * size_units[size_unit])
#         return size_in_bytes
#     else:
#         raise ValueError("Invalid file size unit")
#
#
# def check_path(path):
#     if os.path.exists(path) is False:
#         logging('%s does not exist!' % path)
#         exit()
#     else:
#         return os.path.isfile(path)
#
#
# def check_md5(file_path):
#     # Calculate the MD5 checksum of the file
#     logging("Calculating md5 of: %s" % file_path)
#     md5_hash = hashlib.md5()
#     if os.path.isfile(file_path):
#         with open(file_path, "rb") as file:
#             # Read the file in small chunks to save memory
#             for chunk in iter(lambda: file.read(4096), b""):
#                 md5_hash.update(chunk)
#         return md5_hash.hexdigest()
#     else:
#         return "hash_not_found"
#
#
# def upload(service, path, folder_id, d_folder):
#     if check_path(path) is True:  # file
#         logging('Uploading file from %s to: %s ...' % (path, d_folder))
#         upload_file(service, path, folder_id)
#         logging('Complete uploaded files to gg drive folder: %s - Google Drive folder ID: %s' % (d_folder, folder_id))
#     else:  # folder
#         logging('Uploading files from %s to: %s ...' % (path, d_folder))
#         results = upload_folder(service, path, folder_id)
#
#         if results is False:
#             logging('Upload Failed.')
#         else:
#             logging('Complete uploaded folder to drive folder: %s - FolderID: %s' % (d_folder, folder_id))
#
#
# def isdir(path, x):
#     path = os.path.join(path, x)
#     return os.path.isdir(path)
#
#
# def sort_dir(path):
#     arr = os.listdir(path)
#     arr.sort(key=lambda x: (isdir(path, x), x))
#     return arr
#
#
# def search_file_or_folder(drive_service, name, md5, f_flag):
#     """
#             Search file / folder with name and hash from specific path
#         """
#     page_token = None
#
#     if f_flag == 0:  # folder
#         while True:
#             try:
#                 response = drive_service.files().list(
#                     q="mimeType='application/vnd.google-apps.folder' and trashed=false",
#                     spaces='drive',
#                     fields='nextPageToken, files(id, name)',
#                     pageToken=page_token
#                 ).execute()
#
#             except googleapiclient.errors.HttpError as err:
#                 # Parse error message
#                 message = ast.literal_eval(err.content)['error']['message']
#
#                 if message == 'File not found: ':
#                     logging(message + name, 2)
#                     # Exit with stacktrace in case of other errors
#                     exit(1)
#                 else:
#                     raise
#             for folder in response.get('files', []):
#                 if folder['name'] == name:
#                     return folder['id']
#     elif f_flag == 1:  # file
#         while True:
#             try:
#                 response = drive_service.files().list(
#                     q="mimeType != 'application/vnd.google-apps.folder' and trashed=false and name = '" + name + "'",
#                     spaces='drive',
#                     # includeRemoved=False,
#                     fields='files(id, name, md5Checksum)'
#                 ).execute()
#
#             except googleapiclient.errors.HttpError as err:
#                 # Parse error message
#                 message = ast.literal_eval(err.content)['error']['message']
#
#                 if message == 'File not found: ':
#                     logging(message + name, 2)
#                     # Exit with stacktrace in case of other errors
#                     exit(1)
#                 else:
#                     raise
#
#             filtered_files = [file for file in response.get('files', []) if 'md5Checksum' in file]
#             if len(filtered_files) > 0:
#                 # print(filtered_files)
#                 for item in filtered_files:
#                     if item['md5Checksum'] == str(md5):
#                         return item['md5Checksum']
#                 logging("file are not yet exist on Google Drive (md5 not match), uploading new file...")
#                 return ""
#             else:
#                 logging("file are not yet exist on Google Drive, uploading...")
#                 return ""
#     else:
#         return ""
#
#
# def transfer_ownership(service, folder_id, SA_email):
#     # Define the permission body
#     permission = {
#         'type': 'user',
#         'role': 'owner',
#         'emailAddress': SA_email,
#         # 'pendingOwner': True,
#         'transferOwnership': True
#     }
#
#     try:
#         service.permissions().create(
#             fileId=folder_id,
#             body=permission,
#             transferOwnership=True
#         ).execute()
#         print(
#             "Ownership of the resource has been transferred to the new Service Account {}".format(
#                 SA_email
#             )
#         )
#     except Exception as e:
#         err_msg = "An error occurred while transferring the ownership {}".format(str(e))
#         raise RuntimeError(err_msg)
#
#
#
# def get_folder_id(drive_service, parent_folder_id, d_folder, flag):
#     """
#                 Check if destination folder exists and return its ID
#         """
#
#     page_token = None
#
#     while True:
#         try:
#             parent_folder_id = "'root'"
#             response = drive_service.files().list(
#                 q="mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed = false",
#                 spaces='drive',
#                 fields='nextPageToken, files(id, name)',
#                 pageToken=page_token).execute()
#
#         except googleapiclient.errors.HttpError as err:
#             # Parse error message
#             message = ast.literal_eval(err.content)['error']['message']
#
#             if message == 'File not found: ':
#                 logging(message + d_folder, 2)
#                 # Exit with stacktrace in case of other errors
#                 exit(1)
#             else:
#                 raise
#
#         for folder in response.get('files', []):
#             if folder['name'] == d_folder:
#                 if flag == 'p':
#                     logging("Parent Folder: %s - id: %s" % (folder['name'], folder['id']))
#                 elif flag == 'c':
#                     logging("Destination Folder : %s - id: %s" % (folder['name'], folder['id']))
#                 return folder['id']
#
#         page_token = response.get('nextPageToken', None)
#
#         if page_token is None:
#             break
#
#
# def upload_file(service, file_dir, folder_id):
#     """
#                 Upload files in the local folder to Google Drive
#         """
#
#     mime = magic.Magic(mime=True)
#     file1 = os.path.basename(file_dir)
#
#     # Check the file's size
#     stat_info = stat(file_dir)
#
#     if stat_info.st_size > 0:
#
#         #       print('uploading ' + file1 + '... ')
#
#         # get mime types
#         mine_type = mime.from_file(file_dir)
#
#         # Upload file to folder.
#         media = MediaFileUpload(
#             file_dir,
#             mimetype=mine_type,
#             resumable=True
#         )
#         request = service.files().create(
#             media_body=media,
#             body={'name': file1,
#                   'parents': [folder_id]
#                   }
#         )
#         response = None
#         logging("uploading %s..." % file1)
#         a = 0
#         while response is None:
#             status, response = request.next_chunk()
#             if a == 1:
#                 if status:
#                     previous_progress_message = "Current: %s / Total: %s - %.2f%%" % (
#                         human_bytes(status.resumable_progress), human_bytes(status.total_size), status.progress() * 100)
#                     padding = ' ' * (len(previous_progress_message) + 2)  # Add 2 for the carriage return and space
#
#                     print(padding, end="\r")  # Clear the line
#                     print("Current: %s / Total: %s - %.2f%%" % (
#                         human_bytes(status.resumable_progress), human_bytes(status.total_size),
#                         status.progress() * 100),
#                           end="\r", flush=True)
#                     a = 0
#             elif a == 0:
#
#                 if status:
#                     previous_progress_message = "Current: %s / Total: %s - %.2f%%" % (
#                         human_bytes(status.resumable_progress), human_bytes(status.total_size), status.progress() * 100)
#                     padding = ' ' * (len(previous_progress_message) + 2)  # Add 2 for the carriage return and space
#
#                     print(padding, end="\r")  # Clear the line
#                     print("Current: %s / Total: %s - %.2f%%" % (
#                         human_bytes(status.resumable_progress), human_bytes(status.total_size),
#                         status.progress() * 100),
#                           end="\r", flush=True)
#
#                     # print(str(datetime.now()) + ">
#                     # " + "uploading " + file1 + " ... %d%%." % int(status.progress() * 100), end = "\r")
#
#         # print(str(datetime.now()) + "> " + "uploading " + file1 + " ... 100%. ", end = "\r", flush=True)
#         logging("File %s upload successfully!" % file1)
#         print("\n")
#
#
# #        print("Complete!")
#
#
# def upload_folder(service, path, parent_folder_id):
#     try:
#         chdir(path)
#     except OSError:
#         logging('%s is missing, exiting...' % path, 1)
#         return False
#
#     if not os.listdir(path):
#         logging('Directory is empty, moving to next folder...')
#         return False
#
#     arr = sort_dir(path)
#
#     for name in arr:
#         local_path = os.path.join(path, name)
#         #        print(local_path)
#
#         if os.path.isfile(local_path):
#             md5 = check_md5(local_path)
#             logging("local md5 %s is %s" % (name, md5))
#             search_rs = search_file_or_folder(service, name, md5, 1)
#             logging("ggdr md5 %s is %s" % (name, search_rs))
#             if search_rs == "":
#                 upload_file(service, local_path, parent_folder_id)
#             else:
#                 logging("file already exist on GGDr, skipping... \n")
#                 continue
#
#         elif os.path.isdir(local_path):
#             print('\n')
#             logging('Processing Directory: %s' % local_path)
#
#             fd_id = get_folder_id(service, parent_folder_id, name, 'n')
#             if fd_id is not None:
#                 logging('Folder %s already exist on Google Drive' % name)
#                 logging('checking files on: %s...' % name)
#                 upload_folder(service, local_path, fd_id)
#             else:
#                 logging('Folder %s dont exist on Google Drive, creating...' % name, 1)
#                 n_fd_id = create_folder(service, parent_folder_id, name)
#
#                 if n_fd_id is not None:
#                     logging('Create Folder %s successfully, id: %s' % (name, n_fd_id))
#                     logging('checking files on: %s...' % name)
#                     upload_folder(service, local_path, n_fd_id)
#                 else:
#                     logging('Something definitely wrong while creating folder... Exiting...', 2)
#
#     logging('All files in %s uploaded successfully!' % path)
#
#
# def create_folder(service, p_folder_id, folder_name):
#     file_metadata = {
#         'name': folder_name,
#         'parents': [p_folder_id],
#         'mimeType': 'application/vnd.google-apps.folder'
#     }
#
#     file = service.files().create(
#         body=file_metadata,
#         fields='id'
#     ).execute()
#     return file.get('id')
