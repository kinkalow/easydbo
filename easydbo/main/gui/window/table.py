import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class TableWindow(BaseWindow):
    def __init__(self, tname, util, on_close=None):
        self.tname = tname
        self.util = util
        self.columns = util.get_column(tname)
        self.dbop = util.dbop

        self.on_close = on_close

        self.prefkey = prefkey = f'_table{tname}__'
        self.key_tname = f'{prefkey}.{tname}'
        self.key_columns = [f'{prefkey}.{c}' for c in self.columns]
        self.key_inputs = [f'{prefkey}.{c}.input' for c in self.columns]
        self.key_show = '{prefkey}.show'
        self.key_table = '{prefkey}.table'

        self._create()

    def _create(self):
        layout = [
            [sg.Text(f' {self.tname} ', **attr.text_table, key=self.key_tname)],
            [sg.Text(c, key=self.key_columns[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [sg.InputText('', key=self.key_inputs[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [sg.Text()],
            [sg.Button('Show', key=self.key_show)],
            [sg.Table([['' for _ in range(len(self.columns))]],
                      key=self.key_table,
                      headings=self.columns,
                      auto_size_columns=False,
                      col_widths=[20 for _ in range(len(self.columns))])],
        ]
        self.window = sg.Window(
            f'EasyDBO {self.tname}',
            layout,
            size=(800, 500),
            resizable=True,
            finalize=True,
        )
        return self.window

    def handle(self, event, values):
        if event == self.key_show:
            self.show()

    def close(self):
        self.window.close()
        self.window = None
        self.util.call(self.on_close)

    def show(self):
        cmd = f'SELECT * FROM {self.tname};'
        out = self.dbop.execute(cmd, ret=True)
        self.window[self.key_table].update(out)
