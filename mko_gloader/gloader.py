import os

import utils as utils
from argparse import ArgumentParser
from utils.functions import (
    pathstr_to_list
)

from loader import GLoader


def upload(gd_instance, parser, *args):
    try:
        local_source, google_destination, google_parent, *_ = *args, None, None
        if not os.path.exists(local_source):
            raise parser.error(f"Local path:{local_source} is not a valid path")
        gd_path_arr = pathstr_to_list(google_destination)
        gd_destination_id = gd_instance.check_google_drive_path(gd_path_arr, google_parent, True)
        gloader_instance = GLoader(local_source, gd_path_arr[-1], gd_destination_id)
        gloader_instance.fetch(update_type="Google Drive")
        gloader_instance.push()
    except Exception as err:
        print(err)


def list_files(gd_instance, *args):
    gdrive_tree = utils.Tree()
    gdrive_tree.add(['My Drive'], 'root')
    gd_instance.generate_tree_from_google_drive(gdrive_tree)
    node, _ = gdrive_tree.get_node(
        pathstr_to_list(*args)
    )
    gdrive_tree.traverse_and_print(node)

    if args is None:
        return
    print("-------------------------------------------------------------")
    shared_files = gd_instance.list_shared_files()
    if shared_files:
        shared_name = 'Shared with me'
        gdrive_tree = utils.Tree()
        gdrive_tree.add([shared_name], 'shared')
        for item in shared_files:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                gdrive_tree.add(
                    [shared_name] + [item['name']],
                    item['id'],
                    is_dir=True
                )
                gd_instance.generate_tree_from_google_drive(
                    gdrive_tree, item['id'],
                    [item['name']]
                )
            else:
                gdrive_tree.add(
                    [shared_name] + [item['name']],
                    item['id'],
                    is_dir=False,
                    file_size=item['size']
                )
    gdrive_tree.traverse_and_print()


def main(list_of_args: list = None):
    def pass_args(args: list = None):
        """Parse arguments """
        arg_parser.add_argument('-up', '--upload', nargs='+', type=str,
                                help='Upload from LOCAL_PATH to GOOGLE_DRIVE_PATH, '
                                     'usage: -up /home/user/test/file.1 /docs/test/')
        arg_parser.add_argument('-a', '--access', nargs=3, type=str,
                                help='Grant access to file or folder by id {e-mail} {role} {id}  ')
        arg_parser.add_argument('-lp', '--list-permissions', nargs=1, type=str,
                                help='List folder permission by id')
        arg_parser.add_argument('-dp', '--drop-permissions', nargs=2, type=str,
                                help='Drop folder permission by id')
        arg_parser.add_argument('-r', '--remove', nargs=1, type=str,
                                help='Remove google drive file/folder by id')
        arg_parser.add_argument('-ls', '--list-files', nargs='?', type=str, const='root',
                                help='List files and folders')
        arg_parser.add_argument('-cl', '--clear', nargs='?', type=str, const='root',
                                help='Clear folder bi id')
        arg_parser.add_argument('-lt', '--list_trash', action='store_true',
                                help='List files in trash')
        arg_parser.add_argument('-ct', '--clear-trash', action='store_true',
                                help='Clear trash')
        arg_parser.add_argument('-t', '--test', action='store_true',
                                help='Run test function')
        arg_parser.add_argument('-set', '--settings-path', nargs=1, type=str,
                                help='Set folder to keep ini file with settings')
        arg_parser.add_argument('--drop-settings', action='store_true',
                                help='Drop settings to defaults')
        if args is not None:
            return arg_parser.parse_args(args)
        return arg_parser.parse_args()

    arg_parser = ArgumentParser(description="Utilities to work with Google Drive")

    params = vars(pass_args(list_of_args))

    if not any(params.values()):
        raise arg_parser.error(f"You should set parameters to run")

    if params['settings_path'] is not None:
        utils.ConfigHelper(params['settings_path'][0])
        return
    elif params['drop_settings'] is True:
        conf_help = utils.ConfigHelper()
        conf_help.restore_defaults()

    gd_instance = utils.GoogleDriveHelper()

    if params['upload'] is not None:
        upload(gd_instance, arg_parser, *params['upload'])
    elif params['list_files'] is not None:
        list_files(gd_instance, params['list_files'])
    elif params['remove'] is not None:
        gd_instance.hard_delete_file(params['remove'][0])
    elif params['clear'] is not None:
        gd_instance.cleanup_folder_by_id(params['clear'])
    elif params['list_trash'] is True:
        gd_instance.list_trash()
    elif params['clear_trash'] is True:
        gd_instance.clear_trash()
    elif params['access'] is not None:
        gd_instance.grant_permissions(*params['access'][::-1])
    elif params['list_permissions'] is not None:
        gd_instance.list_permissions(*params['list_permissions'])
    elif params['drop_permissions'] is not None:
        gd_instance.drop_permission(*params['drop_permissions'])
    elif params['test'] is not None:
        list_files(gd_instance, *params['test'])


if __name__ == "__main__":
    main()
