import os
import re
import sys
from datetime import datetime

def extract_argv_flags():
    return [f for f in sys.argv if re.search('^--\S+$', f)]
def print_current_time():
    print('Current Time:', datetime.today().strftime('%m/%d'), datetime.now().strftime('%H:%M:%S'))
def open_in_terminal(exe, flags=None, close_on_success=True):
    command = 'start cmd /k {} {}'.format(sys.executable, exe)
    if flags:
        for f in flags:
            command += ' ' + f
    if close_on_success:
        command += ' ^&^& exit'
    os.system(command)