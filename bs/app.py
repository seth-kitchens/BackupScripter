import PySimpleGUI as sg
from bs.windows.main import WindowMain
from bs.g import style

def app(script_manager, context):
    sg.theme(style.sg_theme)
    window_main = WindowMain(script_manager)
    rv = window_main.open(context)
    return rv