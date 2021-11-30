import PySimpleGUI as sg
from .base import BaseLayout
from ..table import TableWindow
from .common import Attribution as attr

class TableChangeLayout(BaseLayout):
    def __init__(self, util):
        self.util = util

        self.prefkey = prefkey = '_tablechange__.'
        self.key_tnames = [f'{prefkey}{tn}' for tn in util.tnames]
        self.layout = [
            [sg.Button(f' {tn} ', **attr.base_button_with_color_safety, key=self.key_tnames[i])
             for i, tn in enumerate(util.tnames)],
            [sg.Text('')],
        ]
        self.tnames_twins = {}

    def handle(self, event, values):
        if event not in self.key_tnames:
            return
        tname = event.replace(f'{self.prefkey}', '')
        if tname in self.tnames_twins:
            twindow = self.tnames_twins[tname]
        else:
            location = self.window.CurrentLocation()
            twindow = TableWindow(tname, self.util, location,
                                  on_close=[self.on_table_window_close, tname])
            self.tnames_twins.update({tname: twindow})
            self.util.winmgr.add_window(twindow)

    def on_table_window_close(self, tname):
        self.tnames_twins.pop(tname)
