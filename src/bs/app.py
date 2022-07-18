import PySimpleGUI as sg
import psgu

from src.bs.script_data import ScriptDataBS
from src.bs.windows.main import WindowMain
from src.bs import g


def app(script_data:ScriptDataBS, window_context:psgu.WindowContext):
    sg.theme(g.style.sg_theme)
    init_script = g.cli.parsed.file_in
    window_main = WindowMain(script_data, init_script=init_script)
    rv = window_main.open(window_context)
    return rv