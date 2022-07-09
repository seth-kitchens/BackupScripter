import PySimpleGUI as sg

from src.bs.script_data import ScriptDataBS
from src.bs.windows.main import WindowMain
from src.bs import g


def app(script_data:ScriptDataBS, context):
    sg.theme(g.style.sg_theme)
    init_script = g.cli.parsed.file_in
    window_main = WindowMain(script_data, init_script=init_script)
    rv = window_main.open(context)
    return rv