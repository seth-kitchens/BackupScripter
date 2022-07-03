from src.bs.script_data import ScriptDataBS

from src.gp import uprint
from src.gp import utils as gp_utils
from src.bs.script import data as b_data, create as b_create
from src.bs import g

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
    backup_success = b_create.create_backup(pre_data, script_data)
    uprint.thin_line()
    print('Backup End')
    uprint.line()
    
    # Results

    if not backup_success:
        print('Result: FAILURE')
        print('Backup execution returned with failure')
        print('')
        if not g.is_noinput():
            gp_utils.prompt_any_input('Enter anything to exit')
        return

    post_data = b_data.PostExecutionData(script_data, pre_data)
    
    if not post_data.backup_success:
        print('Result: FAILURE')
        if not g.is_noinput():
            gp_utils.prompt_any_input('Enter anything to exit')
        return

    print('Result: SUCCESS')

    uprint.line()


    print('Created Backup Details')
    uprint.thin_line()
    post_data.print_details(script_data, pre_data)
    uprint.line()
    if not g.is_noinput():
        gp_utils.prompt_any_input('Enter anything to exit.')
        uprint.line()
    return
