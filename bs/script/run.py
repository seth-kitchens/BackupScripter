import os.path

from gplib.cmd import utils as cmd_utils
from gplib.text.utils import up
from gplib.fs import utils as fs_utils
from bs.fs.vfs import VFSBS as VFS
from bs.script import data as b_data, details as b_details, create as b_create
from bs import g
from bs.fs.matching_group import MatchingGroup

def run(script_manager):
    # Preparation

    script_data = script_manager.to_dict()
    vfs_static = VFS()
    execution_data = {}

    b_data.clean_invalids(script_data)

    execution_data['ResolvedDateSuffix'] = fs_utils.DateString.process(script_data['BackupFileNameDate'])
    execution_data['DestFileName'] = script_data['BackupFileName'][0] + execution_data['ResolvedDateSuffix'] + script_data['BackupFileName'][1]
    execution_data['DestPath'] = os.path.normpath(os.path.join(script_data['BackupDestination'], execution_data['DestFileName']))
    execution_data['VfsStatic'] = vfs_static

    # Inclusion

    vfs_static.build_from_ie_lists(script_data['IncludedItems'], script_data['ExcludedItems'])
    vfs_final = vfs_static.clone()
    vfs_final.process_matching_groups_dict(script_data['MatchingGroupsList'])
    vfs_final.make_ie_lists(script_data)
    vfs_final.save_data_to_dict(script_data)
    execution_data['VfsFinal'] = vfs_final

    # Data Collection

    b_data.collect_pre_execution_info(execution_data, script_data)

    # Display / Confirmation

    if not b_details.confirm_pre_execution_info(execution_data, script_data):
        up.print_line()
        up.print('Backup cancelled.')
        if not g.is_noinput():
            cmd_utils.prompt_any_input('Enter anything to exit')
        return
    up.print()

    # Backup Creation
    
    success = b_create.create_backup(execution_data, script_data)
    if not success:
        up.print_line()
        up.print('Backup failed.')
        if not g.is_noinput():
            cmd_utils.prompt_any_input('Enter anything to exit')
        return

    # Post Execution Testing

    up.print('Post Backup Testing...')

    # Results

    up.print('Backup Finished!')
    up.print_line()
    up.print('Backup Results')
    up.print()
    if not g.is_noinput():
        cmd_utils.prompt_any_input('Enter anything to exit.')
    up.print_line()
    return
