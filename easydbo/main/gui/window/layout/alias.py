import PySimpleGUI as sg
from .base import BaseLayout

class AliasTab(BaseLayout):
    def __init__(self, winmgr, prefkey, util):

        self.aliases = aliases = util.aliases
        self.prefkey = prefkey

        placeholder_mark = '?'
        self.key_btns = [f'{prefkey}.{a.name}.buttons' for a in aliases]
        self.key_inputs = [f'{prefkey}.{a.name}.inputtext' for a in aliases]
        self.key_mark = []
        self.key_reset = f'{prefkey}.reset'

        font13 = ('', 13)

        maxlen = max(len(a.name) for a in aliases)
        layout = []
        for i, a in enumerate(aliases):
            n_qestionmark = len(a.sql.split(placeholder_mark)) - 1
            layout.append([
                sg.Button(a.name, key=self.key_btns[i], font=font13, size=(maxlen, 1)),
                sg.InputText(a.sql, key=self.key_inputs[i], font=font13, expand_x=True, size=(100, 1)),
            ])
            # placeholders
            if n_qestionmark > 0:
                keys = [f'{prefkey}.{a.name}.mark.{j}' for j in range(n_qestionmark)]
                self.key_mark.append(keys)
                layout.append(
                    [sg.Button('', key=self.key_btns[i], font=font13, size=(maxlen, 1))]
                    + [sg.InputText('', key=keys[j], font=font13, size=(19, 1)) for j in range(n_qestionmark)]
                )
        #
        layout = [
            [sg.Button('Reset', key=self.key_reset, font=font13)],
            [sg.Column(layout, pad=(0, 0), expand_x=True, size=(500, 600),
                       scrollable=True, vertical_scroll_only=True)],
        ]

        self.layout = layout

    def handle(self, event, values):
        pass
