import PySimpleGUI as sg
from .base import BaseWindow
from .common.layout.attribution import Attribution as attr

class SaveAsAliasWindow(BaseWindow):
    def __init__(self, pack, query, location):
        super().__init__(pack.winmgr)

        # Layout
        prefkey = self.make_prefix_key('saveasalias', timestamp=True)
        self.key_save = f'{prefkey}save'
        self.key_alias = f'{prefkey}alias'
        self.key_query = f'{prefkey}query'
        self.layout = [
            [
                sg.Button('Save', **attr.base_button_with_color_safety),
                sg.Button('Close', **attr.base_button_with_color_safety),
            ],
            [
                sg.Text('Alias', **attr.base_text, size=(5, 1)),
                sg.InputText('', **attr.base_inputtext, key=self.key_alias),
            ],
            [
                sg.Text('Query', **attr.base_text, size=(5, 1)),
                sg.Multiline(query, **attr.base_multiline, key=self.key_alias, expand_x=True, expand_y=True, size=(1300, 500)),
            ],
        ]

        # Window
        self._window = sg.Window(
            'EasyDBO SaveAsAlias',
            self.layout,
            size=(1300, 500),
            resizable=True,
            finalize=True,
            location=location,
        )

    #def handle(self, event, values):
    #    pass
