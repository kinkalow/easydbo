import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

#class SaveAsAliasLayout(BaseLayout):
#    def __init__(self):
#        self.layout = [
#            [
#                sg.Alias(f'Query', key=self.key_query_btn),
#                sg.InputText(cmd, key=self.key_query_txt)
#            ],
#        ]

class SaveAsAliasWindow(BaseWindow):
    def __init__(self, winmgr, util, query, parent_loc=None):
        super().__init__()

        # Layout
        prefkey = util.make_timestamp_prefix('saveasalias')
        self.key_save = f'{prefkey}save'
        self.key_alias = f'{prefkey}alias'
        self.key_query = f'{prefkey}query'
        self.layout = [
            [
                sg.Button('Save', **attr.base_button_with_color_safety),
                sg.Button('Close', **attr.base_button_with_color_safety),
            ],
            [
                sg.Text('Alias', size=(5, 1)),
                sg.InputText('', key=self.key_alias),
            ],
            [
                sg.Text('Query', size=(5, 1)),
                sg.Multiline(query, key=self.key_alias, expand_x=True, expand_y=True, size=(1000, 500)),
            ],
        ]

        # Window
        self.window = sg.Window(
            'EasyDBO SaveAsAlias',
            self.layout,
            size=(1000, 500),
            resizable=True,
            finalize=True,
        )
        if parent_loc:
            self.window.move(parent_loc[0], parent_loc[1] + 30)

    #def handle(self, event, values):
    #    if event == self.key:
