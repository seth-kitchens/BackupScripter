import PySimpleGUI as sg
from bs.script_data import ScriptDataBS
from bs.windows.main import WindowMain
from bs.g import style

def app(script_data:ScriptDataBS, context):
    sg.theme(style.sg_theme)
    window_main = WindowMain(script_data)
    rv = window_main.open(context)
    return rv