import PySimpleGUI as sg
from .base import BaseLayout
from .common import Attribution as attr
from ..query import QueryResultWindow

class AliasTab(BaseLayout):
    def __init__(self, winmgr, prefkey, util):
        self.util = util
        self.aliases = aliases = util.aliases
        self.prefkey = prefkey

        placeholder_mark = '?'
        self.key_btns = [f'{prefkey}{a.name}.button' for a in aliases]
        self.key_inputs = [f'{prefkey}{a.name}.inputtext' for a in aliases]
        self.key_mark = []  # Define below
        self.key_reset = f'{prefkey}reset'

        maxlen = max(len(a.name) for a in aliases)
        layout = []
        for i, a in enumerate(aliases):
            n_qestionmark = len(a.sql.split(placeholder_mark)) - 1
            layout.append([
                sg.Button(a.name, **attr.base_button_with_color_safety, key=self.key_btns[i], size=(maxlen, 1)),
                sg.InputText(a.sql, **attr.base_inputtext, key=self.key_inputs[i], expand_x=True, size=(100, 1)),
            ])
            # placeholders
            if n_qestionmark > 0:
                keys = [f'{prefkey}{a.name}.mark.{j}' for j in range(n_qestionmark)]
                self.key_mark.append(keys)
                layout.append(
                    [sg.Button('', **attr.base_button_with_color_safety, key=self.key_btns[i], size=(maxlen, 1))]
                    + [sg.InputText('', **attr.base_inputtext, key=keys[j], size=(19, 1)) for j in range(n_qestionmark)]
                )
        #
        layout = [
            [sg.Button('Reset', **attr.base_button_with_color_safety, key=self.key_reset)],
            [sg.Column(layout, pad=(0, 0), expand_x=True, size=(500, 600),
                       scrollable=True, vertical_scroll_only=True)],
        ]

        self.layout = layout

    def handle(self, event, values):
        if event in self.key_btns:
            key = '.'.join(event.split('.')[:-1] + [self.key_inputs[0].split('.')[-1]])
            self.query(values[key])

    def query(self, sql):
        from easydbo.main.select.sql import execute_query
        query, header, data = execute_query(self.util.dbop, sql)
        win = QueryResultWindow(self.util.winmgr, self.util, query, header, data)
        self.util.winmgr.add_window(win)
