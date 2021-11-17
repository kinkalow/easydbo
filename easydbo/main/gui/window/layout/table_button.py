import PySimpleGUI as sg
from .base import BaseLayout
from ..table import TableWindow

class TableButtonLayout(BaseLayout):
    def __init__(self, winmgr, prefkey, util):
        self.winmgr = winmgr
        self.prefkey = prefkey
        self.util = util

        self.key_tnames = [f'{prefkey}{tn}' for tn in util.tnames]
        self.layout = [
            [sg.Button(f' {tn} ', key=self.key_tnames[i], font=('', 13), button_color='#b8b846')
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
            twindow = TableWindow(tname, self.util,
                                  on_close=[self.on_table_window_close, tname])
            self.tnames_twins.update({tname: twindow})
            self.winmgr.add_window(twindow)

    def on_table_window_close(self, tname):
        self.tnames_twins.pop(tname)
