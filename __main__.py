import sys
argv = tuple(sys.argv)

import psgu

from src.bs import g
from src.bs.app import app
from src.bs.script.main import run_script
from src.bs.script_data import ScriptDataBS
from src.bs.windows.main import WindowMain
from src.gp import utils as gp_utils


if __name__ != '__main__':
    sys.exit()

g.cli.parse_args(argv)
if g.cli.parsed.debug and not g.cli.parsed.noterm:
    g.cli.open_new_terminal(__file__)


def run():
    if g.cli.parsed.backup or g.cli.parsed.getdata:
        run_script()
    else:
        run_editor()


def run_editor():
    window_context = psgu.WindowContext()
    WindowMain.open_loading_window(window_context, title='Backup Scripter')    
    if g.cli.parsed.debug:
        gp_utils.print_current_time()
    script_data = ScriptDataBS()
    script_data.load_save_file()
    app(script_data, window_context)


run()
