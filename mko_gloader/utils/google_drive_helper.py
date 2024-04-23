import io
import os
import pickle
import traceback  # Import traceback module for detailed error information
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
from .logger import Logger
from .config_helper import ConfigHelper


class GoogleDriveHelper:

    def __init__(self,
                 local_source: [str, os.PathLike] = None,
                 destination_folder: str = None,
                 destination_parent_id: str = None,
                 cred_path: [str, os.PathLike] = None,
                 use_token: bool = None,
                 scopes=None
                 ):

        self.configuration = ConfigHelper()
        self.logger = Logger()

        cred_path = cred_path or self.configuration.credentials_path
        use_token = use_token or self.configuration.use_token
        scopes = scopes or self.configuration.scopes
        init_creds = self._set_credentials(cred_path, use_token, scopes)
        self.service = self.initialize_service(init_creds)
        self.destination_folder_name = destination_folder if destination_folder else 'root'
        self.parent_folder_id = destination_parent_id if destination_parent_id else 'root'
        self.local_filesystem_folder_path = local_source if local_source else ''

    def _set_credentials(self, cred_path, use_token, scopes):
        if os.path.isfile(cred_path):
            current_dir = os.path.abspath(os.path.dirname(cred_path))
            if use_token:
                token_file = os.path.join(current_dir, 'token.pickle')
                return self.get_credentials_token(cred_path, token_file, scopes)
            else:
                return self.get_credentials_service(cred_path, scopes)
        else:
            print(f"Can't find: {cred_path}, please check settings.")
            self.logger.error(f"Can't find: {cred_path}, please check settings.")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise FileNotFoundError

    def get_credentials_token(self, credentials_json, token_file, scopes):
        try:
            credentials = None
            # The file token.pickle stores the user's access and refresh tokens and is
            # created automatically when the authorization flow completes for the first time.
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    credentials = pickle.load(token)

            # If there are no (valid) credentials available, let the user log in.
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_json, scopes)
                    credentials = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(credentials, token)

            return credentials

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in get_credentials_token: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def get_credentials_service(self, credentials_json, scopes):
        """Authenticate to Google API using service account"""

        credentials = service_account.Credentials.from_service_account_file(
            filename=credentials_json,
            scopes=scopes)

        return credentials

    def initialize_service(self, credentials):
        try:
            # Create a Google Drive API service using the saved or new credentials
            print("============================================\nInitializing Google Drive service ...")
            gd_service = build('drive', 'v3', credentials=credentials)
            print("Initializing Complete!\n============================================")
            return gd_service
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in initialize_service: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def list_google_drive_folders(self):
        folders = None
        try:
            folders = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    self.service.files()
                    .list(
                        q="mimeType='application/vnd.google-apps.folder' and trashed = false",
                        spaces='drive',
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        fields='nextPageToken, files(id, name)',
                        pageToken=page_token,
                    )
                    .execute()
                )
                folders.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
        except Exception as error:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_google_drive: {error}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
        finally:
            return folders

    def list_shared_files(self):
        data = None
        try:
            data = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    self.service.files()
                    .list(
                        q="sharedWithMe = True",
                        spaces='drive',
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        fields='nextPageToken, files(id, name, mimeType, trashed, size)',
                        pageToken=page_token,
                    )
                    .execute()
                )
                data.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
        except Exception as error:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_google_drive: {error}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
        finally:
            return data

    def get_child_folder_id_by_name(self, folder_name, parent_id=None, create=False):
        if parent_id is None:
            parent_id = self.parent_folder_id
        try:
            results = self.service.files().list(
                q=f"mimeType='application/vnd.google-apps.folder' and trashed=false"
                  f" and '{parent_id}' in parents  and name = '{folder_name}'",
                fields="files(id)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageSize=1000,
            ).execute()
            item = results.get('files', [])
            if len(item) > 1:
                self.logger.error(f"Multiple folders with same name found: {item}")
                raise ValueError(f"Multiple folders with same name found: {item}")
            if not item and create is False:
                self.logger.error(f"No directory with the name: {folder_name}")
                raise ValueError(f"No directory with the name: {folder_name}")
            elif not item and create is True:
                item = [{'id': self.create_folder(folder_name, parent_id)}]
            return item[0]['id']

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_google_drive: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def check_google_drive_path(self, path_arr, parent_id=None, create=False):
        last_id = parent_id
        for folder_name in path_arr:
            last_id = self.get_child_folder_id_by_name(folder_name, last_id, create)
        return last_id

    def generate_tree_from_google_drive(self, tree_root, parent_id=None, path=None):
        if parent_id is None:
            parent_id = self.parent_folder_id
        if path is None:
            path = []
        try:
            results = self.service.files().list(
                q=f"'{parent_id}' in parents and trashed=false",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, trashed, size)"
            ).execute()
            items = results.get('files', [])

            for i, item in enumerate(items):
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    tree_root.add(
                        [self.destination_folder_name] + path + [item['name']],
                        item['id'],
                        is_dir=True
                    )
                    self.generate_tree_from_google_drive(
                        tree_root,
                        item['id'],
                        path + [item['name']]
                    )
                else:
                    tree_root.add(
                        [self.destination_folder_name] + path + [item['name']],
                        item['id'], is_dir=False,
                        file_size=item['size']
                    )
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_google_drive: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def upload_file(self, file_path, folder_id):
        try:
            file_name = os.path.basename(file_path)
            media_body = MediaFileUpload(self.local_filesystem_folder_path + file_path, resumable=True)
            request = self.service.files().create(
                supportsAllDrives=True,
                media_body=media_body,
                body={
                    'name': file_name,
                    'parents': [folder_id]
                }
            )
            response = None
            print(f"===============================\nStarting upload for: {file_name}")
            while response is None:
                status, response = request.next_chunk()
            print(f"Upload complete!\nFile path: {file_path}\n===============================")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in upload_file: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def create_folder(self, folder_name, parent_folder_id):
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            folder = self.service.files().create(
                supportsAllDrives=True,
                body=folder_metadata,
                fields='id'
            ).execute()
            return folder['id']
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in create_folder: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def create_folders_for_upload(self, names, parent_folder_id):
        try:
            last_id = parent_folder_id
            for name in names:
                folder_metadata = {
                    'name': name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [last_id]
                }
                folder = self.service.files().create(
                    supportsAllDrives=True,
                    body=folder_metadata,
                    fields='id'
                ).execute()
                last_id = folder['id']
            return last_id
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in create_folders_for_upload: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def upload_folder(self, folder_path, parent_folder_id):
        try:
            folder_name = os.path.basename(folder_path)
            folder_id = self.create_folder(folder_name, parent_folder_id)

            for item in os.listdir(self.local_filesystem_folder_path + folder_path):
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(self.local_filesystem_folder_path + item_path):
                    self.upload_file(item_path, folder_id)
                elif os.path.isdir(self.local_filesystem_folder_path + item_path):
                    self.upload_folder(item_path, folder_id)

            print(
                f"===============================\nUpload complete for folder: {folder_name}.\n"
                f"===============================")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in upload_folder: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def upload_helper(self, gdrive_tree, folder_path):
        try:
            folder_path = folder_path[0]
            to_upload_path = folder_path.split("/")
            nearest_node, folders_already_created = gdrive_tree.get_node(to_upload_path[1:])
            final_id = nearest_node.id
            if folders_already_created != len(to_upload_path[1:-1]):
                final_id = self.create_folders_for_upload(to_upload_path[folders_already_created + 1:], nearest_node.id)
            self.upload_file(folder_path, final_id) if not os.path.isdir(
                self.local_filesystem_folder_path + folder_path) else self.upload_folder(
                folder_path, final_id)
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in upload_helper: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def bulk_delete(self, ids):
        def callback(request_id, response, exception):
            if not exception:
                print(response)
            else:
                print(exception)

        for i in range(0, len(ids), 100):
            batch = self.service.new_batch_http_request(callback=callback)
            for file_id in ids[i:i + 100]:
                batch.add(self.service.files().delete(fileId=file_id))
            try:
                print(batch.execute())
            except Exception as error:
                self.logger.error(f"Error occurred in bulk_delete: {error}")
                # Optionally, log the full traceback for detailed error information
                self.logger.error(traceback.format_exc())
                # Raise the exception again to notify the caller about the error

    def cleanup_folder_by_id(self, folder_id):
        files_to_delete = self.list_content_by_id(folder_id)
        ids = [file['id'] for file in files_to_delete]
        self.bulk_delete(ids)

    def list_content_by_id(self, folder_id):
        content = None
        try:
            content = []
            page_token = None
            while True:
                # pylint: disable=maybe-no-member
                response = (
                    self.service.files()
                    .list(
                        q=f"'{folder_id}' in parents and trashed = false",  # mimeType='application/vnd.google-apps' and
                        spaces='drive',
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        fields='nextPageToken, files(id, name)',
                        pageToken=page_token,
                    )
                    .execute()
                )
                content.extend(response.get("files", []))
                page_token = response.get("nextPageToken", None)
                if page_token is None:
                    break
        except Exception as error:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_google_drive: {error}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
        finally:
            return content

    def hard_delete_file(self, file_id):
        try:
            self.service.files().delete(
                supportsAllDrives=True,
                fileId=file_id
            ).execute()
            print(f"File/Folder with ID {file_id} deleted successfully.")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in hard_delete_file: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def delete_file(self, file_id, gdrive_tree=None):
        try:
            body_value = {'trashed': True}
            self.service.files().update(
                supportsAllDrives=True,
                fileId=file_id,
                body=body_value
            ).execute()

            parent_node_of_file = gdrive_tree.find_parent_node_by_id(file_id)
            if parent_node_of_file:
                for file_name in parent_node_of_file.children:
                    if parent_node_of_file.children[file_name].id == file_id:
                        del parent_node_of_file.children[file_name]
                        break

            print(f"File/Folder with ID {file_id} moved to trash successfully.")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in delete_file: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def download_file(self, output_path, drive_file_id):
        try:
            request = self.service.files().get_media(
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fileId=drive_file_id
            )

            dir_path = (self.local_filesystem_folder_path + output_path).removesuffix(
                os.path.basename((self.local_filesystem_folder_path + output_path)))
            os.makedirs(dir_path, exist_ok=True)

            with io.FileIO(self.local_filesystem_folder_path + output_path, 'wb') as output_file:
                downloader = MediaIoBaseDownload(output_file, request)
                done = False

                print(f"===============================\nStarting download for: {output_path.split('/')[-1]}")

                while not done:
                    status, done = downloader.next_chunk()

            print(f"Download complete!\nFile saved to: {output_path}\n===============================")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in download_file: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def download_folder(self, output_path, drive_folder_id):
        try:
            os.makedirs(self.local_filesystem_folder_path + output_path, exist_ok=True)

            results = self.service.files().list(
                q=f"parents in '{drive_folder_id}'",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                fields="files(id, name, mimeType)"
            ).execute()
            items = results.get('files', [])

            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    subfolder_path = os.path.join(output_path, item['name'])
                    self.download_folder(subfolder_path, item['id'])
                else:
                    file_path = os.path.join(output_path, item['name'])
                    self.download_file(file_path, item['id'])

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in download_folder: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def download_helper(self, output_path, drive_folder_id, is_dir):
        try:
            if not is_dir:
                self.download_file(output_path, drive_folder_id)
            else:
                self.download_folder(output_path, drive_folder_id)
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in download_helper: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def list_trash(self):
        try:
            results = self.service.files().list(
                q=f"trashed=True",
                fields="files(id,name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            items = results.get('files', [])
            if not items:
                print("No trashed files.")
            else:
                for item in items:
                    print(f"{item['name']}: {item['id']}")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in list_trash: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def clear_trash(self):
        try:
            self.service.files().emptyTrash().execute()
            print("All trash cleaned up")
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in clear_trash: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def grant_permissions(self, file_id: str, role: str, email: str):
        try:
            permission = {
                'type': 'user',
                'role': role,
                'emailAddress': email
            }
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in grant_permissions: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def list_permissions(self, file_id, drop=False):
        page_token = None
        permission_list = []
        try:
            while True:
                response = self.service.permissions().list(
                    fileId=file_id,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                    fields='permissions/id,permissions/displayName,permissions/role,permissions/emailAddress',
                    pageToken=page_token,
                ).execute()
                permission_list.extend(response.get('permissions', []))
                if page_token is None:
                    break
            if len(permission_list) == 1 and permission_list[0]['role'] == 'owner':
                print('No permissions provided except ownership')
                return
            for permission in permission_list:
                if permission['role'] != 'owner':  # put ids and emails for non-owner in a list
                    print(permission)
                    if drop:
                        print('dropped!')
                        self.drop_permission(file_id, permission['id'])
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in list_permissions: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def drop_permission(self, file_id, permission_id):
        # delete perms using the id
        try:
            self.service.permissions().delete(
                fileId=file_id,
                permissionId=permission_id,
                supportsAllDrives=True
            ).execute()

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in drop_permission: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e
