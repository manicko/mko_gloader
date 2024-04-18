import logging
from datetime import datetime

LOGS_FOLDER_PATH = './logs'


class Logger:
    """
    A simple logger class for logging information and errors to a file.

    Usage:
    logger = Logger()
    logger.info("This is an information message.")
    logger.error("This is an error message.")
    """

    def __init__(self, logs_folder_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %I:%M:%S %p')
        if logs_folder_path:
            file_handler = logging.FileHandler(
                LOGS_FOLDER_PATH + "/" + datetime.now().strftime("%d-%m-%y") + ".log")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            file_handler.close()

    def info(self, message):
        """
        Log an information message.

        Parameters:
        - message: The information message to be logged.
        """
        self.logger.info(message)

    def error(self, message):
        """
        Log an error message.

        Parameters:
        - message: The error message to be logged.
        """
        self.logger.error(message)
