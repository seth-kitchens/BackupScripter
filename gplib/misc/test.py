import PySimpleGUI as sg

def test():
    layout = [[sg.In('TEST', text_color='black', background_color='#ddaaff')]]
    window = sg.Window('Test', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
test()