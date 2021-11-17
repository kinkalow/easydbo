import PySimpleGUI as sg
from .base import BaseWindow

#class ResultLayout():
#    pass

class SelectResultWindow(BaseWindow):
    def __init__(self, winmgr, util, query, headings, data):
        super().__init__()
        self.winmgr = winmgr
        self.util = util
        self.query = query

        length = len(data[0])

        self.prefkey = prefkey = util.make_timestamp_prefix('result')
        self.key_query_btn = f'{prefkey}querybutton'
        self.key_query_txt = f'{prefkey}querytext'

        self.layout = [
            [
                sg.Button(f'Query', key=self.key_query_btn),
                sg.Text(query, key=self.key_query_txt),
            ],
            [
                sg.Table(
                    data,
                    headings=headings,
                    justification='right',
                    selected_row_colors='red on yellow',
                    expand_x=True,
                    expand_y=True,
                    key=None,
                    auto_size_columns=False,
                    col_widths=[20 for _ in range(length)],
                )
            ],
        ]

        self.window = sg.Window(
            'EasyDBO SelectResult',
            self.layout,
            location=(4500, 200),
            size=(1000, 300),
            resizable=True,
            finalize=True
        )

    def handle(self, event, values):
        if event == self.key_query_btn:
            from .save_as_alias import SaveAsAliasWindow
            location = self.window.CurrentLocation()
            win = SaveAsAliasWindow(self.winmgr, self.util, self.query, parent_loc=location)
            self.winmgr.add_window(win)
