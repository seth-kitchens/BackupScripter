from pathlib import Path
import sys
import os
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

import nssgui as nss

from gplib.project import utils as project_utils
#from gplib.project import logging

from bs.app import app
from bs import g
from bs.script_data import ScriptDataManagerBS as sdm_bs
from bs.windows.main import WindowMain

argv_flags = project_utils.extract_argv_flags()

if __name__ == "__main__":
    context = nss.WindowContext()
    WindowMain.open_loading_window(context, title='Backup Scripter')
    #logging.init_logging('Starting Log: EDITOR', g.paths.dirs.logs)
    #logging.info('flags: ' + str(argv_flags))
    
    if g.flags.DEBUG in argv_flags:
        project_utils.print_current_time()
    script_manager = sdm_bs()
    app(script_manager, context)
