import os
import shutil
import traceback
from datetime import datetime
from .logger import Logger
from .config_helper import ConfigHelper


class FilesystemHelper:
    """
    A utility class for interacting with the filesystem, including generating trees and performing soft deletes.

    Usage:
    filesystem_helper = FilesystemHelper()
    filesystem_helper.generate_tree_from_filesystem(tree)
    filesystem_helper.soft_delete_from_filesystem("/example/file.txt")
    """

    def __init__(self, source_folder_path, backup_folder_path: str = None):
        """
        Initialize FilesystemHelper with folder and backup paths.
        """
        self.configuration = ConfigHelper()
        self.logger = Logger()
        self.SOURCE_FOLDER_PATH = source_folder_path
        self.BACKUP_FOLDER_PATH = backup_folder_path


    def generate_tree_from_filesystem(self, tree):
        """
        Generate a tree structure based on the current filesystem.

        Parameters:
        - tree: An instance of the Tree class to store the filesystem structure.
        """
        try:
            # Function to add files and subdirectories to the tree
            root_value = os.path.basename(self.SOURCE_FOLDER_PATH)
            tree.add([root_value])

            def add_recursive(current_node, current_path):
                for item in os.listdir(current_path):
                    item_path = os.path.join(current_path, item)
                    if os.path.isdir(item_path):
                        # If it's a directory, add it as a child and recurse
                        child_value = os.path.basename(item_path)
                        tree.add(current_node + [child_value])
                        add_recursive(current_node + [child_value], item_path)
                    else:
                        # If it's a file, add it directly
                        # Get Given File Size
                        file_size = os.path.getsize(item_path)
                        tree.add(current_node + [item], file_size=file_size)

            # Start the traversal from the root of the tree
            add_recursive([root_value], self.SOURCE_FOLDER_PATH)

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in generate_tree_from_filesystem: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def soft_delete_from_filesystem(self, path):
        """
        Soft delete a file or directory from the filesystem.

        Parameters:
        - path: The path of the file or directory to be soft deleted.
        """
        try:
            backup_dir_name = datetime.now().strftime('%d-%m-%Y')
            os.makedirs(f"{self.BACKUP_FOLDER_PATH + '/' + backup_dir_name}", exist_ok=True)

            if os.path.exists(self.SOURCE_FOLDER_PATH + path):
                dir_path = self.BACKUP_FOLDER_PATH + "/" + datetime.now().strftime(
                    '%d-%m-%Y') + "/" + "/".join(path.split("/")[:-1])
                os.makedirs(dir_path, exist_ok=True)

                shutil.move(self.SOURCE_FOLDER_PATH + path, dir_path)
                print("Deleted Successfully!")
                print(f"Path: {self.SOURCE_FOLDER_PATH + path}")
                print(f"Backup path: {dir_path}")
            else:
                print(f"Path does not exist: {self.SOURCE_FOLDER_PATH + path}")

            print("============================================")

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in soft_delete_from_filesystem: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e

    def hard_delete_from_filesystem(self, path):
        """
        Soft delete a file or directory from the filesystem.

        Parameters:
        - path: The path of the file or directory to be soft deleted.
        """
        try:

            file_path = self.SOURCE_FOLDER_PATH + path
            if os.path.exists(file_path):
                os.remove(file_path)
                print("Hard Deleted Successfully!")
                print(f"Path: {file_path}")
            else:
                print(f"Path does not exist: {file_path}")

            print("============================================")

        except Exception as e:
            # Log the error using the logger
            self.logger.error(f"Error occurred in hard_delete_from_filesystem: {e}")
            # Optionally, log the full traceback for detailed error information
            self.logger.error(traceback.format_exc())
            # Raise the exception again to notify the caller about the error
            raise e
