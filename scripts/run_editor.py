from pathlib import Path
import sys
import os
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

import nssgui as nss

from gplib import utils as gp_utils
#from gplib.project import logging

from bs.app import app
from bs import g
from bs.script_data import ScriptDataBS
from bs.windows.main import WindowMain

argv_flags = gp_utils.extract_argv_flags()

if __name__ == "__main__":
    context = nss.WindowContext()
    WindowMain.open_loading_window(context, title='Backup Scripter')
    #logging.init_logging('Starting Log: EDITOR', g.paths.abs.dirs.logs)
    #logging.info('flags: ' + str(argv_flags))
    
    if g.flags.DEBUG in argv_flags:
        gp_utils.print_current_time()
    script_data = ScriptDataBS()
    script_data.load_save_file()
    app(script_data, context)
