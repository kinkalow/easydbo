import PySimpleGUI as sg
import re
from .base import BaseWindow
from .layout.common import Attribution as attr

class FilterWindow(BaseWindow):
    def __init__(self, tname, columns, tdata, util, parent_loc):
        self.columns = columns
        self.tdata = tdata
        self.util = util

        prefkey = util.make_timestamp_prefix(f'table{tname}filter')
        self.key_tname = f'{prefkey}{tname}'
        self.key_columns = [f'{prefkey}{c}' for c in self.columns]
        self.key_inputs = [f'{prefkey}{c}.input' for c in self.columns]
        self.key_filter = f'{prefkey}filter'
        self.key_clear = f'{prefkey}clear'
        self.key_reset = f'{prefkey}reset'
        self.key_table = f'{prefkey}table'

        max_col = 5
        max_row = (len(columns) - 1) // max_col + 1
        text_inputtext = []
        for i in range(max_row):
            s1, s2 = i * max_col, (i + 1) * max_col
            cols = self.columns[s1: s2]
            text_inputtext.append([
                [sg.Text(c, **attr.base_text_with_size, key=self.key_columns[i]) for i, c in enumerate(cols)],
                [sg.InputText('', **attr.base_inputtext_with_size, key=self.key_inputs[i]) for i, c in enumerate(cols)],
            ])
        layout = [
            [sg.Text(f' {tname} ', **attr.text_table, key=self.key_tname)],
        ] + text_inputtext + [
            [sg.Button('Filter', **attr.base_button_with_color_safety, key=self.key_filter),
             sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_clear)],
            [sg.Text('')],
        ] + [
            [sg.Button('Reset', **attr.base_button_with_color_safety, key=self.key_reset)],
            [sg.Table(
                tdata,
                **attr.base_table,
                key=self.key_table,
                headings=columns,
                col_widths=[20 for _ in range(len(columns))],
            )],
        ]

        self.window = sg.Window(
            'EasyDBO Filter',
            layout,
            size=(1200, 500),
            resizable=True,
            finalize=True,
        )
        self.window.move(parent_loc[0], parent_loc[1] + 30)

        self.table = self.window[self.key_table]

    def handle(self, event, values):
        if event == self.key_filter:
            self.filter(values)
        elif event == self.key_clear:
            self.clear(values)
        elif event == self.key_reset:
            self.reset()

    def filter(self, values):
        inputs = {k.split('.')[1]: v for k, v in values.items() if v and k in self.key_inputs}
        keys, values = map(list, zip(*inputs.items()))
        idxes = [self.columns.index(k) for k in keys]
        tdata = []
        for d in self.tdata:
            for i, v in zip(idxes, values):
                if not re.search(f'.*{v}.*', str(d[i])):
                    break
            else:
                tdata.append(d)
        self.window[self.key_table].update(tdata)

    def clear(self, values):
        [self.window[k].update('') for k, v in values.items() if v and k in self.key_inputs]

    def reset(self):
        self.window[self.key_table].update(self.tdata)
