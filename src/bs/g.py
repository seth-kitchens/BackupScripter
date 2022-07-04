import sys
import os
from pathlib import Path

from src.scriptlib.packfio import PackFIO
from data.project.packfio_data import packfio_data


class flags:
    DEBUG = '--debug'
    DBGCMD = '--dbgcmd'
    EDITOR = '--editor'
    BACKUP = '--backup'
    GETDATA = '--getdata'
    NOINPUT = '--noinput'
def exe_mode():
    if flags.EDITOR in sys.argv:
        return 'editor'
    elif flags.BACKUP in sys.argv:
        return 'backup'
def is_editor(): return flags.EDITOR in sys.argv
def is_backup(): return flags.BACKUP in sys.argv
def is_debug(): return flags.DEBUG in sys.argv
def is_noinput(): return flags.NOINPUT in sys.argv

def update_g(cls_lib:type, cls_project:type, name, value=None):
    if value != None:
        setattr(cls_project, name, value)
    setattr(cls_lib, name, cls_project.__dict__[name])

_project_path = str(Path(__file__).parent.parent.parent)
def project_path(relpath):
    return os.path.normpath(os.path.join(_project_path, relpath))

class paths:
    class rel:
        class files:
            script_data = 'data/project/script_data.json'
            initial_script = 'backup.py' # loaded at start
            template_script = 'backup.py'
            packfio_data = 'data/project/packfio_data.py'
        class dirs:
            packing = 'temp/packing'
            logs = 'logs'
    class abs:
        class files:
            script_data = project_path('data/project/script_data.json')
            initial_script = project_path('backup.py') # loaded at start
            template_script = project_path('backup.py')
            packfio_data = project_path('data/project/packfio_data.py')
        class dirs:
            project = _project_path
            packing = project_path('temp/packing')
            logs = project_path('logs')\


packfio_files_to_pack = {
    paths.rel.files.script_data
}
packfio = PackFIO(packfio_files_to_pack, packfio_data)


# Variables

class variables:
    pass
gv = variables

def update_member(obj, d, name):
    if name in d and name in dir(obj):
        obj.__dict__[name] = d[name]

class style:
    name = 'py'
    sg_theme = 'DarkBlue3'
    class colors:
        error = 'red'
        warning = 'orange'
        header = 'gold'
        valid = 'white'
        invalid = 'lightgray'
    def load(st:dict|str):
        if isinstance(st, str):
            d_style = style.styles.__dict__[st]
        else:
            d_style = st
        def load(name):
            update_member(style, d_style, name)
        load('name')
        load('sg_theme')
        if 'colors' in d_style:
            def load_color(name):
                update_member(style.colors, d_style['colors'], name)
            load_color('error')
            load_color('warning')
            load_color('header')
            load_color('valid')
            load_color('invalid')
    class styles:
        py = {
            'sg_theme': 'DarkBlue3',
            'colors': {
                'error': 'red',
                'warning': 'orange',
                'header': 'gold',
                'valid': 'white',
                'invalid': 'lightgray'
            }
        }
        gray_out = {
            'sg_theme': 'DarkBlue3',
            'colors': {
                'error': 'red',
                'warning': 'orange',
                'header': 'gold',
                'valid': 'white',
                'invalid': 'lightgray'
            }
        }
        boring = {
            'sg_theme': 'Default1',
            'colors': {
                'error': 'red',
                'warning': 'orange',
                'header': 'black'
            }
        }
colors = style.colors