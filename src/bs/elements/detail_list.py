from abc import ABC, abstractmethod

import PySimpleGUI as sg

import nssgui as nss


__all__ = ['DetailListBS']


class DetailListBS(nss.ge.DetailList, ABC):

    def __init__(self, object_id, lstrip=' \n', rstrip=' \n'):
        super().__init__(object_id, lstrip, rstrip)
    
    ### GuiElement

    # Layout

    def get_row_buttons_main_top(self):
        size = (10, 1)
        row = super().get_row_buttons_main_top()
        row.append(sg.Button('Preview Here', key=self.keys['PreviewHere'], size=size))
        row.append(sg.Button('Resolve Here', key=self.keys['ResolveHere'], size=size))
        return row

    def get_row_buttons_main_bottom(self):
        size = (10, 1)
        row = super().get_row_buttons_main_bottom()
        row.append(sg.Button('Preview All', key=self.keys['PreviewAll'], size=size))
        row.append(sg.Button('Resolve All', key=self.keys['ResolveAll'], size=size))
        return row
    
    # Data

    # Keys and Events

    def define_keys(self):
        super().define_keys()
        self.add_key('PreviewHere')
        self.add_key('ResolveHere')
        self.add_key('PreviewAll')
        self.add_key('ResolveAll')
    
    def define_menus(self):
        super().define_menus()
        rcms = self.right_click_menus
        rcms.unlock()
        rcms['ListboxItem']['PreviewHere']('Preview Here')
        rcms['ListboxItem']['ResolveHere']('Resolve Here')
        rcms.lock()
    
    def define_events(self):
        super().define_events()

    ### DetailList

    ### DetailListBS

