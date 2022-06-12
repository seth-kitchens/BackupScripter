from pathlib import Path
import sys
import os
project_dir = str(Path(__file__).parent.parent)
os.chdir(project_dir)
sys.path.append(project_dir)

if not '--dbgcmd' in sys.argv:
    pyfile = os.path.normpath('scripts/' + os.path.basename(sys.argv[0]))
    command = 'start cmd /k {} {} --dbgcmd'.format(sys.executable, pyfile)
    os.system(command)
    sys.exit()

import tests
tests.run()