from pathlib import Path
import sys
import os
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

if '--editor' in sys.argv:
    action = '--editor'
elif '--backup' in sys.argv:
    action = '--backup'

command = 'start cmd /k {} __main__.py {} --debug --dbgcmd ^&^& exit'.format(sys.executable, action)
os.system(command)