import os
import utils as utils
import traceback


class GLoader:
    """
    GSpace is a utility for synchronizing files between the local filesystem and Google Drive.

    Usage:
    gloader_instance = GLoader()
    gloader_instance.pull()
    gloader_instance.push()
    gloader_instance.sync()
    """

    logger = utils.Logger()

    def __init__(self, local_source: [str, os.PathLike] = None, google_destination: str = None,
                 google_parent: str = None):
        """
        Initialize GSpace by creating instances of GoogleDriveHelper,
        FilesystemHelper, and initializing Google Drive service.
        """
        try:
            self.local_source = local_source

            self.logger.info("Program Started")
            self.gdrive = utils.GoogleDriveHelper(local_source, google_destination, google_parent)
            self.filesystem = utils.FilesystemHelper(local_source) if local_source else None
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in GSpace initialization: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def fetch(self, update_type="Local Filesystem"):
        """
        Fetch changes from Google Drive and local filesystem, and print the differences.

        Parameters:
        - update_type: Type of update, either "Local Filesystem" or "Google Drive".
        """
        try:
            gdrive_tree, local_fs_tree = utils.Tree(), utils.Tree()
            gdrive_tree.add([self.gdrive.destination_folder_name], self.gdrive.parent_folder_id)
            self.gdrive.generate_tree_from_google_drive(gdrive_tree)
            self.filesystem.generate_tree_from_filesystem(local_fs_tree)
            # gdrive_tree.traverse_and_print()
            # local_fs_tree.traverse_and_print()
            changes_in_local = local_fs_tree.find_difference_path(gdrive_tree)
            changes_in_server = gdrive_tree.find_difference_path(local_fs_tree)
            print("============================================")

            print("Following changes will take place in " + update_type)

            if update_type == "Local Filesystem":
                print(f"Additions ({len(changes_in_server['Additions'])}):")
                for change in changes_in_server["Additions"]:
                    print("+", change[0])
                print(f"Modifications ({len(changes_in_server['Modifications'])}):")
                for change in changes_in_server["Modifications"]:
                    print("*", change[0])
                print(f"Deletions ({len(changes_in_server['Deletions'])}):")
                for change in changes_in_server["Deletions"]:
                    print("-", change[0])
            else:
                print(f"Additions ({len(changes_in_local['Additions'])}):")
                for change in changes_in_local["Additions"]:
                    print("+", change[0])
                print(f"Modifications ({len(changes_in_local['Modifications'])}):")
                for change in changes_in_server["Modifications"]:
                    print("*", change[0])
                print(f"Deletions ({len(changes_in_local['Deletions'])}):")
                for change in changes_in_local["Deletions"]:
                    print("-", change[0])

            print("============================================")

            return changes_in_local, changes_in_server, gdrive_tree, local_fs_tree
        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in fetch: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def pull(self):
        """
        Pull changes from Google Drive to the local filesystem.
        """
        try:
            changes_in_local, changes_in_server, gdrive_tree, local_fs_tree = self.fetch()

            if (not changes_in_server["Additions"] and not changes_in_server["Deletions"]
                    and not changes_in_server["Modifications"]):
                print("============================================")
                print("No changes to pull!\nExiting ...")
                return print("============================================")

            confirmation = ""

            while confirmation not in ["yes", "no"]:
                confirmation = input("Are you sure you want to continue? [yes, no]\n >>> ")
                if confirmation not in ["yes", "no"]:
                    print("Usage: 'yes' or 'no'")

            if confirmation == "no":
                print("============================================")
                print("Canceled by user!\nExiting ...")
                return print("============================================")

            if len(changes_in_server["Additions"]):
                print("============================================")
                print("Starting pulling changes from Google Drive:")
                for to_download in changes_in_server["Additions"]:
                    self.gdrive.download_helper(to_download[0], to_download[1], to_download[2])

            if len(changes_in_server["Modifications"]):
                print("============================================")
                print("Starting modifications in local Filesystem:")
                print("============================================")

                for to_modify in changes_in_server["Modifications"]:
                    self.filesystem.hard_delete_from_filesystem(to_modify[0])
                    self.gdrive.download_helper(to_modify[0], to_modify[1], to_modify[2])

                print("Finished modification changes from Google Drive!")
                print("============================================")

            if len(changes_in_server["Deletions"]):
                print("============================================")
                print("Starting removing files in local Filesystem:")
                for to_delete in changes_in_server["Deletions"]:
                    self.filesystem.soft_delete_from_filesystem(to_delete[0])

                print("Finished removing files from local Filesystem!")
                print("============================================")

            print("SUCCESS: Pulled Google Drive!")
            self.logger.info("Pulled from google drive")

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in pull: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def push(self):
        """
        Push changes from the local filesystem to Google Drive.
        """
        try:
            changes_in_local, changes_in_server, gdrive_tree, local_fs_tree = self.fetch(update_type="Google Drive")

            if (not changes_in_local["Additions"] and not changes_in_local["Deletions"]
                    and not changes_in_local["Modifications"]):
                print("============================================")
                print("No changes to push!\nExiting ...")
                return print("============================================")

            confirmation = "yes"  # change to "" to ask user

            while confirmation not in ["yes", "no"]:
                confirmation = input("Are you sure you want to continue? [yes, no]\n >>> ")
                if confirmation not in ["yes", "no"]:
                    print("Usage: 'yes' or 'no'")

            if confirmation == "no":
                print("============================================")
                print("Canceled by user!\nExiting ...")
                return print("============================================")

            if len(changes_in_local["Additions"]):
                print("============================================")
                print("Starting pushing changes to Google Drive:")
                for to_upload in changes_in_local["Additions"]:
                    self.gdrive.upload_helper(gdrive_tree, to_upload)

                print("Finished pushing changes to Google Drive!")
                print("============================================")

            if len(changes_in_server["Modifications"]):
                print("============================================")
                print("Starting modifications in Google Drive:")
                print("============================================")

                for to_modify in changes_in_server["Modifications"]:
                    self.gdrive.delete_file(to_modify[1], gdrive_tree=gdrive_tree)
                    self.gdrive.upload_helper(gdrive_tree, to_modify)

                print("Finished modifications in Google Drive!")
                print("============================================")

            if len(changes_in_local["Deletions"]):
                print("============================================")
                print("Starting removing files from Google Drive:")
                for to_delete in changes_in_local["Deletions"]:
                    self.gdrive.delete_file(to_delete[1], gdrive_tree=gdrive_tree)

                print("Finished removing files from Google Drive!")
                print("============================================")

            print("SUCCESS: Pushing to Google Drive!")
            self.logger.info("Pushed to Google Drive")

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in push: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def sync(self):
        """
        Synchronize changes between the local filesystem and Google Drive.
        """
        try:
            self.pull()
            self.push()

            self.logger.info("Sync from Google Drive and Local System Completed")

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in sync: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e
