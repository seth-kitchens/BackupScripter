from pathlib import Path
import sys
import os
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

from gplib import utils as gp_utils
#from gplib.project import logging

from bs.script.app import app
from bs import g
from bs.script_data import ScriptDataBS

argv_flags = gp_utils.extract_argv_flags()

if __name__ == "__main__":
    #logging.init_logging('Starting Log: BACKUP', g.paths.abs.dirs.logs)
    #logging.info('flags: ' + str(argv_flags))
    if g.flags.DEBUG in argv_flags:
        gp_utils.print_current_time()
    script_data = ScriptDataBS()
    script_data.load_save_file()
    if g.flags.GETDATA in argv_flags:
        script_data.get_data()
    else:
        app(script_data)
