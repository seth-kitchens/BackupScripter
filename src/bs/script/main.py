import sys
argv = tuple(sys.argv)
from pathlib import Path
import os
project_dir = str(Path(__file__).parent.parent.parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

from src.gp import utils as gp_utils

from src.bs.script.app import app
from src.bs import g
from src.bs.script_data import ScriptDataBS

g.cli.parse_args(argv)

def run_script():
    if g.cli.parsed.debug:
        gp_utils.print_current_time()
    script_data = ScriptDataBS()
    script_data.load_save_file()
    if g.cli.parsed.getdata:
        script_data.get_data()
    else:
        app(script_data)

if __name__ == "__main__":
    run_script()
