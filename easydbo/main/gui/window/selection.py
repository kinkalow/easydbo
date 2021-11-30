import PySimpleGUI as sg
from .base import BaseWindow
from .layout.table_change import TableChangeLayout
from .layout.alias import AliasTab
from .layout.fulljoin import FullJoinTab

class SelectionWindow(BaseWindow):
    def __init__(self, winmgr, util):
        super().__init__()

        # Layout
        tblchg = TableChangeLayout(util)
        fulljoin = FullJoinTab(util)
        alias = AliasTab(util)
        self.prefkey_clsobj = {tblchg.prefkey: tblchg,
                               fulljoin.prefkey: fulljoin,
                               alias.prefkey: alias}
        layout = [
            tblchg.get_layout(),
            [sg.TabGroup([[
               sg.Tab('FullJoin', fulljoin.get_layout()),
               sg.Tab('Alias', alias.get_layout()),
            ]], expand_x=True, expand_y=True)]
        ]

        self.window = sg.Window(
            'EasyDBO Selection',
            layout,
            location=(5000, 200),
            size=(1200, 800),
            resizable=True,
            finalize=True,
        )
        for clsobj in self.prefkey_clsobj.values():
            clsobj.set_window(self.window)

        #self.window['-key_join_frame-'].Widget.configure(highlightcolor='yellow', highlightthickness=2)

    def handle(self, event, values):
        for p, c in self.prefkey_clsobj.items():
            if event.startswith(p):
                c.handle(event, values)
                break
