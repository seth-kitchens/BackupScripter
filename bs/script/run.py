import os.path

from gplib.cmd import utils as cmd_utils
from gplib.text.utils import up
from gplib.fs import utils as fs_utils
from bs.script import data as b_data, details as b_details, create as b_create
from bs import g
from bs.fs.matching_group import MatchingGroup

def run(script_manager):
    # Preparation

    script_data = script_manager.to_dict()

    b_data.clean_invalids(script_data)

    # Data Collection

    pe_data = b_data.collect_pe_data(script_data)

    # Display / Confirmation

    if not b_details.confirm_pe_data(pe_data, script_data):
        up.print_line()
        up.print('Backup cancelled.')
        if not g.is_noinput():
            cmd_utils.prompt_any_input('Enter anything to exit')
        return
    up.print()

    # Backup Creation
    
    success = b_create.create_backup(pe_data, script_data)
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
