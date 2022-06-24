import os.path
from bs.script_data import ScriptDataBS

from gplib import uprint
from gplib import utils as gp_utils
from bs.script import data as b_data, create as b_create
from bs import g
from bs.fs.matching_group import MatchingGroup

def run(script_data:ScriptDataBS):
    # Preparation

    b_data.clean_invalids(script_data)

    # Pre-Execution Data

    pre_data = b_data.PreExecutionData(script_data)

    if not pre_data.confirm_data(script_data):
        uprint.line()
        print('Backup cancelled.')
        if not g.is_noinput():
            gp_utils.prompt_any_input('Enter anything to exit')
        return
    print()

    # Backup Creation
    
    uprint.line()
    print('Backup Start')
    uprint.thin_line()
    success = b_create.create_backup(pre_data, script_data)
    uprint.thin_line()
    print('Backup End')
    uprint.line()
    if not success:
        print('Backup failed.')
        if not g.is_noinput():
            gp_utils.prompt_any_input('Enter anything to exit')
        return

    print('Backup Finished!')
    uprint.line()

    # Results

    post_data = b_data.PostExecutionData(script_data, pre_data)

    print('Backup Results')
    uprint.thin_line()
    post_data.print_details(script_data, pre_data)
    uprint.line()
    if not g.is_noinput():
        gp_utils.prompt_any_input('Enter anything to exit.')
        uprint.line()
    return
