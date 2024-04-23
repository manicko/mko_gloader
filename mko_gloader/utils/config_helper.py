# python 3.x
import os
from configparser import ConfigParser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

CONVERTERS = {
    'list': lambda x: [i.strip() for i in x.split(',')] if len(x) > 0 else []
}
PATH_KEEPER = 'path_to_config.ini'
PATH_KEEPER_DEFAULTS = {
    'PathToConfig':
        {
            'path': ''
        }
}

CONFIG_NAME = 'config.ini'
CONFIG_DEFAULTS = {
    'Logs': {
        'logs_path': '',
        'keep_logs': True
    },
    'GoogleDriveAPI': {
        'cred_path': '',
        'use_token': False,
        'scopes': [
            'https://www.googleapis.com/auth/drive'
        ]
    },

}


class ConfigHelper:
    def __init__(self, config_folder: str | None = None):

        self.config_path = self.get_config(config_folder)

        # Gloader Settings
        self.config_reader = ConfigParser(converters=CONVERTERS)
        self.config = Path.joinpath(self.config_path, CONFIG_NAME)

        # GoogleDriveAPI Settings
        self.use_token = None
        self.credentials_path = None
        self.scopes = None

        # Logs Settings
        self.logs_folder_path = None
        self.keep_logs = None
        self.check_configuration()

    def get_config(self, config_folder: str | None = None):
        keeper_reader = ConfigParser()
        keeper_path = Path.joinpath(ROOT_DIR, PATH_KEEPER)

        if config_folder:
            PATH_KEEPER_DEFAULTS['PathToConfig']['path'] = config_folder
            self.set_configuration(keeper_reader, keeper_path, PATH_KEEPER_DEFAULTS)

        if Path.exists(keeper_path):
            keeper_reader.read(keeper_path)
            config_path = keeper_reader.get('PathToConfig', 'path', fallback=None)
            if config_path and self.path_exist(config_path):
                return Path(config_path)

        self.set_configuration(keeper_reader, keeper_path, PATH_KEEPER_DEFAULTS)
        print("Path to config folder is not set. Please use the '-set' key to set it.")
        exit()

    @staticmethod
    def set_configuration(reader, config_path: str | os.PathLike,
                          configuration: dict[str, dict[str, str | bool | int | list | None]]):
        for section, params in configuration.items():
            if not reader.has_section(section):
                reader.add_section(section)
            for k, v in params.items():
                val = str(v) if not isinstance(v, list) else ', '.join(map(str, v))
                reader.set(section, k, val)
        with open(config_path, 'w') as config:
            reader.write(config)

    @staticmethod
    def path_exist(setting_folder):
        try:
            setting_folder = Path(setting_folder).resolve()
            if Path.exists(setting_folder):
                return True

            confirmation = ''
            while confirmation not in ["yes", "no"]:
                confirmation = input(f"The path specified is not exist. "
                                     f"Create folder '{str(setting_folder)}'? "
                                     f"[yes, no]\n >>> ")
                if confirmation not in ["yes", "no"]:
                    print("Usage: 'yes' or 'no'")

            if confirmation == "no":
                print("============================================")
                print("Canceled by user!\nExiting ...")
                print("============================================")
                return False
            else:
                Path.mkdir(setting_folder)
                return True
        except Exception as e:
            print("============================================")
            print(f"Failed to create folder '{setting_folder}'")
            print(f"Error {e} occurred")
            print("============================================")
            return False

    def check_configuration(self):
        try:
            if not Path.is_file(self.config):
                self.restore_defaults()
                print(f'Please configure {self.config} before usage')
            else:
                self.config_reader.read(self.config)

                # GoogleDriveAPI Settings
                self.credentials_path = self.config_reader.get('GoogleDriveAPI', 'cred_path')
                self.use_token = self.config_reader.getboolean('GoogleDriveAPI', 'use_token')
                self.scopes = self.config_reader.getlist('GoogleDriveAPI', 'scopes')

                # Logs Settings
                self.keep_logs = self.config_reader.getboolean('Logs', 'keep_logs')
                self.logs_folder_path = self.config_reader.get('Logs', 'logs_path')

                check_config = True
                if not Path.is_file(Path(self.credentials_path)):
                    print(f"Credentials file is not found. Check path to credentials in {self.config}")
                    check_config = False
                if self.keep_logs and (not self.logs_folder_path or not Path.is_dir(Path(self.logs_folder_path))):
                    print(f"Logs folder is not found. Check path to Logs folder in in {self.config}")
                    check_config = False
                if check_config:
                    return
        except Exception as err:
            self.restore_defaults()
            print(f'Error: {err}, restoring default settings.')
        exit()

    def restore_defaults(self):
        self.set_configuration(self.config_reader, self.config, CONFIG_DEFAULTS)
