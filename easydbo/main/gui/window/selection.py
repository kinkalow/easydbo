import PySimpleGUI as sg
from .base import BaseWindow
from .selection_layout.table_change import TableChangeLayout
from .selection_layout.alias import AliasLayout
from .selection_layout.fulljoin import FullJoinLayout

class SelectionWindow(BaseWindow):
    def __init__(self, util):
        super().__init__(util.winmgr)

        # Layout
        tblchg = TableChangeLayout(self, util)
        fulljoin = FullJoinLayout(self, util)
        alias = AliasLayout(self, util)
        self.prefkey_clsobj = {tblchg.get_privatekey(): tblchg,
                               fulljoin.get_privatekey(): fulljoin,
                               alias.get_privatekey(): alias}
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
