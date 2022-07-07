import sys
argv = sys.argv
from pathlib import Path
import os
import argparse
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

arg_parser = argparse.ArgumentParser('run_tests')
arg_parser.add_argument('--noterm', action='store_true', help='Without this, file is reopened in terminal')
class parsed:
    noterm:bool = None
arg_parser.parse_args(argv[1:], parsed)

if not parsed.noterm:
    pyfile = os.path.normpath('scripts/' + os.path.basename(sys.argv[0]))
    command = 'start cmd /k {} {} --noterm'.format(sys.executable, pyfile)
    os.system(command)
    sys.exit()

import tests
tests.run()