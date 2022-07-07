import sys
argv = tuple(sys.argv)
from pathlib import Path
import os
import argparse
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

# parse args

arg_parser = argparse.ArgumentParser('run_debug')
arg_parser.add_argument('--editor', action='store_true')
arg_parser.add_argument('--backup', action='store_true')
class parsed:
    editor:bool = None
    backup:bool = None
arg_parser.parse_args(argv[1:], parsed)

# run backup scripter

command_args = [
    'start cmd /k', sys.executable, '__main__.py --debug'
]

if parsed.backup:
    command_args.append('--backup')
elif parsed.editor:
    pass
else:
    arg_parser.error('Must use "--editor" or "--backup" flag')

command_args.append('--noterm')

command_args.extend([
    '^&^& exit'
])

os.system(' '.join(command_args))