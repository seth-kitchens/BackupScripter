# Create windows shortcuts

import os
from collections import namedtuple
import sys


script_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(script_dir)


ShortcutData = namedtuple('ShortcutData', ['destname', 'srcname', 'args'])


data = [
    ShortcutData('_test_editor', 'run_debug.py', '--editor'),
    ShortcutData('_test_backup', 'run_debug.py', '--backup'),
    ShortcutData('_run_tests', 'run_tests.py', None),
    ShortcutData('_cmd_bs', 'cmd_bs.py', None)
]
temp_bat=os.path.join(script_dir, '__temp__.bat')


# based on https://superuser.com/questions/392061
def make_py_shortcut(sd:ShortcutData):
    src = os.path.join(script_dir, sd.srcname)
    dest = os.path.join(script_dir, sd.destname)
    if not dest.lower().endswith('.lnk'):
        dest += '.lnk'
    target = sys.executable
    args = src if sd.args == None else '{} {}'.format(src, sd.args)
    if not os.path.exists(target):
        print('python exe not found:', target)
        return
    if not os.path.exists(src):
        print('src not found:', src)
        return
    if os.path.exists(dest):
        print('dest already exists, can\'t overwrite:', dest)
        return
    pws_commands = [
        '$ws = New-Object -ComObject WScript.Shell',
        '$s = $ws.CreateShortcut(%SHORTCUT%)',
        '$S.TargetPath = %TARGET%',
        '$S.Arguments = %ARGUMENTS%',
        '$S.WorkingDirectory = %WORKDIR%',
        '$S.Save()',
    ]
    pws_command = '"{}"'.format(';'.join(pws_commands))
    batch_commands = [
        "set TARGET='{}'".format(target),
        "set SHORTCUT='{}'".format(dest),
        "set ARGUMENTS='{}'".format(args),
        "set WORKDIR='{}'".format(script_dir),
        'set PWS=powershell.exe -ExecutionPolicy Bypass -NoLogo -NonInteractive -NoProfile',
        '%PWS% -Command ' + pws_command
    ]
    with open(temp_bat, 'w') as file_out:
        file_out.write('\n'.join(batch_commands))
    os.system(temp_bat)
    os.remove(temp_bat)
    print('created', os.path.basename(dest))


for sd in data:
    make_py_shortcut(sd)
if os.path.exists(temp_bat):
    os.remove(temp_bat)
