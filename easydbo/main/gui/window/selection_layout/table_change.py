import PySimpleGUI as sg
from .base import BaseLayout
from ..table import TableWindow
from ..layout.common import Attribution as attr

class TableChangeLayout(BaseLayout):
    def __init__(self, selwin, util):
        self.selwin = selwin
        self.util = util
        self.table_windows = {tname: None for tname in util.tnames}

        self.prefkey = prefkey = '_tablechange__.'
        self.key_tables = [f'{prefkey}{t}' for t in util.tnames]

        self.layout = [
            [sg.Button(f' {tn} ', **attr.base_button_with_color_warning, key=self.key_tables[i])
             for i, tn in enumerate(util.tnames)],
            [sg.Text('')],
        ]

    def handle(self, event, values):
        if event in self.key_tables:
            tname = event.split('.')[-1]
            self.open_table(tname)

    def open_table(self, tname):
        if self.table_windows[tname] in self.util.winmgr.windows:
            return
        location = self.selwin.get_location(dy=80)
        win = TableWindow(tname, self.util, location)
        self.util.winmgr.add_window(win)
        self.table_windows[tname] = win.get_window()
