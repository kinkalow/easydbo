import PySimpleGUI as sg
from .base import BaseWindow

class ShowWindow(BaseWindow):
    def __init__(self, cmd=None, headings=None, data=None, key=None):
        super().__init__()
        length = len(data[0])
        self.layout = [
            [sg.Text(f'Query: {cmd}')],
            [sg.Table(
            data,
            headings=headings,
            justification='right',
            selected_row_colors='red on yellow',
            expand_x=True,
            expand_y=True,
            key=key,
            auto_size_columns=False,
            col_widths=[20 for _ in range(length)],
            )],
        ]

        self._create()

    def _create(self):
        self.window = sg.Window(
            'EasyDBO Result',
            self.layout,
            location=(4500, 200),
            size=(1000, 300),
            resizable=True,
            finalize=True
        )
