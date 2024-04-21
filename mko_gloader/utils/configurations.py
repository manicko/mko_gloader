# python 3.x
from os import PathLike
from configparser import ConfigParser
from pathlib import Path
from logger import Logger

ROOT_DIR = Path(__file__).resolve().parent
PATH_KEEPER = 'path_to_config.ini'
CONFIG_NAME = 'config.ini'

CONVERTERS = {
    'list': lambda x: [i.strip() for i in x.split(',')] if len(x) > 0 else []
}
DEFAULTS = {
    'Logs': {
        'logs_path': None,
        'keep_logs': True
    },
    'GoogleDriveAPI': {
        'cred_path': None,
        'use_token': False,
        'scopes': [
            'https://www.googleapis.com/auth/drive'
        ]
    },

}


class ConfigHelper:
    def __init__(self):


        self.config_path = None
        self.keeper_reader = ConfigParser()
        self.config_reader = ConfigParser(converters=CONVERTERS)
        self.path_keeper = Path.joinpath(ROOT_DIR, PATH_KEEPER)
        self.check_configuration()

        # Google Drive API Settings
        # self.config_reader.read(PATH_KEEPER)
        #
        # self.config_file = Path.joinpath(ROOT_DIR, CONFIG_NAME)
        #
        # self.use_token = config.getboolean('GoogleDriveAPI', 'use_token')
        # self.credentials_path = config.get('GoogleDriveAPI', 'cred_path')
        # self.scopes = config.getlist('GoogleDriveAPI', 'scopes')
        # # General Settings
        # self.logs_folder_path = config.get('Logs', 'logs_path')
        # self.keep_logs = config.getboolean('Logs', 'keep_logs')
        #
        # # Google Drive API Settings
        # USE_TOKEN = config.getboolean('GoogleDriveAPI', 'use_token')
        # CREDENTIALS_PATH = config.get('GoogleDriveAPI', 'cred_path')
        # SCOPES = config.getlist('GoogleDriveAPI', 'scopes')
        # # General Settings
        # LOGS_FOLDER_PATH = config.get('Logs', 'logs_path')
        # KEEP_LOGS = config.getboolean('Logs', 'keep_logs')

    def check_configuration(self):
        if not Path.exists(self.path_keeper):
            self._set_path_keeper()
        self.keeper_reader.read(self.path_keeper)
        if not self.keeper_reader.has_section('PathToConfig'):
            self._set_path_keeper()
        self.config_path = self.keeper_reader.get('PathToConfig', 'path', fallback=None)
        if not self.config_path:
            print('Configuration is not set')


    def _set_path_keeper(self):
        self.keeper_reader.add_section('PathToConfig')
        self.keeper_reader.set('PathToConfig', 'path', None)
        with open(self.path_keeper, 'w') as f:
            self.keeper_reader.write(f)

    def is_set(setting_folder):
        if Path.exists(setting_folder):
            return True
        confirmation = ''
        while confirmation not in ["yes", "no"]:
            confirmation = input(f"Create folder '{setting_folder}'? [yes, no]\n >>> ")
            if confirmation not in ["yes", "no"]:
                print("Usage: 'yes' or 'no'")

        if confirmation == "no":
            print("============================================")
            print("Canceled by user!\nExiting ...")
            print("============================================")
            return False
        else:
            try:
                Path.mkdir(setting_folder)
                return True
            except Exception as e:
                print("============================================")
                print(f"Failed to create folder '{setting_folder}'")
                print("============================================")
                return False

    def set_config_path(self, setting_folder):
        if self.is_set(setting_folder):
            paths = Path.joinpath(ROOT_DIR, self.path_keeper)
            c = ConfigParser()
            c.add_section('PathToConfig')
            c.set('PathToConfig', 'path', setting_folder)
            with open(paths, 'w') as f:
                c.write(f)
            return True
        return False

    CONFIG_FILE = Path.joinpath(setting_folder, 'gloader_config.ini')

    def add_settings(**kwargs):
        for section, params in DEFAULTS.items():
            if not config.has_section(section):
                config.add_section(section)
            for k, v in params.items():
                if section in kwargs and k in kwargs[section]:
                    if isinstance(kwargs[section][k], list):
                        val = ', '.join(map(str, kwargs[section][k]))
                    else:
                        val = str(kwargs[section][k])
                    config.set(section, k, val)
        try:
            with open(CONFIG_FILE, 'w') as conf:
                config.write(conf)
        except FileNotFoundError as err:
            print('Configuration file is not found in ')

    def restore_defaults():
        add_settings(**DEFAULTS)
