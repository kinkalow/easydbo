import PySimpleGUI as sg
from .base import BaseWindow
from .layout.table_button import TableButtonLayout
from .layout.alias import AliasTab
from .layout.fulljoin import FullJoinTab

class SelectWindow(BaseWindow):
    def __init__(self, winmgr, util):
        super().__init__()

        # Layout
        self.prefkey_instbl = '_instbl__.'
        self.prefkey_fulljoin = '_fulljoin__.'
        self.prefkey_alias = '_alias__.'
        instbl = TableButtonLayout(winmgr, self.prefkey_instbl, util)
        fulljoin = FullJoinTab(winmgr, self.prefkey_fulljoin, util)
        alias = AliasTab(winmgr, self.prefkey_alias, util)
        self.prefkey_clsobj = {self.prefkey_instbl: instbl,
                               self.prefkey_fulljoin: fulljoin,
                               self.prefkey_alias: alias}
        layout = [
            instbl.get_layout(),
            [sg.TabGroup([[
               sg.Tab('FullJoin', fulljoin.get_layout()),
               sg.Tab('Alias', alias.get_layout()),
            ]], expand_x=True)]
        ]

        self.window = sg.Window(
            'EasyDBO select',
            layout,
            location=(5000, 200),
            size=(1300, 800),
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
