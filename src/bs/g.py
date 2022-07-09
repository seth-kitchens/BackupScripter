import os
import argparse
from pathlib import Path

from src.scriptlib.packfio import PackFIO
from data.project.packfio_data import packfio_data
from src.gp import utils as gp_utils

class cli:
    
    argv:tuple = None
    arg_parser:argparse.ArgumentParser = None

    class parsed:
        file_in:str|None = None
        debug:bool = None
        noterm:bool = None
        backup:bool = None
        getdata:tuple[str, str] = None
        noinput:bool = None

    def get_file_in():
        return cli.parsed.file_in

    def getdata_file():
        if not cli.parsed.getdata:
            raise RuntimeError('no --getdata in args')
        return cli.parsed.getdata[0]

    def open_new_terminal(src:str):
        args = list(cli.argv)
        if not cli.parsed.noterm:
            args.append('--noterm')
        gp_utils.open_in_terminal(src, args)

    def parse_args(args:tuple):
        cli.argv = args
        cli.arg_parser.parse_args(cli.argv[1:], cli.parsed)
        getdata = cli.parsed.getdata
        if getdata:
            getdata[0] = os.path.normpath(getdata[0])

    def __init__(self):
        raise RuntimeError('Class is not instantiatable')


arg_parser = cli.arg_parser = argparse.ArgumentParser(prog='BackupScripter')
arg_parser.add_argument('file_in', nargs='?', default=None)
arg_parser.add_argument('--noterm', action='store_true',
    help='Without this, --debug will cause program to be reopened in terminal')
arg_parser.add_argument('--debug', action='store_true')
arg_parser.add_argument('--backup', action='store_true')
arg_parser.add_argument('--getdata', nargs=1, action='store')
arg_parser.add_argument('--noinput', action='store_true')
# call parse_args in __main__.py


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
            packing = 'output/temp/packing'
            logs = 'logs'

    class abs:

        class files:
            script_data = project_path('data/project/script_data.json')
            initial_script = project_path('backup.py') # loaded at start
            template_script = project_path('backup.py')
            packfio_data = project_path('data/project/packfio_data.py')

        class dirs:
            project = _project_path
            packing = project_path('output/temp/packing')
            logs = project_path('logs')\


packfio_files_to_pack = {
    paths.rel.files.script_data
}
packfio = PackFIO(packfio_files_to_pack, packfio_data)


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
