import re
import PySimpleGUI as sg
from easydbo.output.print_ import SimplePrint as SP
from .attribution import Attribution as attr

class FilterLayout():
    def __init__(self, prefix_key, columns, key_table, dbop, query, display_columns=False):
        """
        prefix_key         : str        : Prefix for key
        columns            : List(str)  : List with column names as elements
        key_table          : str        : Key for sg.Table
        dbop               : object     : Database operation object
        query              : str        : Query database to restore original data

        NOTE: Caller must call self.set_window method of callee
        """
        self.columns = columns
        self.query = query
        self.key_table = key_table
        self.dbop = dbop

        self.prefkey = prefkey = f'{prefix_key}filter.'
        self.key_inputs = [f'{prefkey}{c}.input' for c in columns]
        self.key_filter = f'{prefkey}filter'
        self.key_clear = f'{prefkey}clear'
        self.key_reset = f'{prefkey}reset'

        #max_col = 5
        #max_row = (len(columns) - 1) // max_col + 1
        #text_inputtext = []
        #for i in range(max_row):
        #    s1, s2 = i * max_col, (i + 1) * max_col
        #    cols = self.columns[s1: s2]
        #    text_inputtext.append([sg.InputText('', **attr.base_inputtext_with_size, key=self.key_inputs[i]) for i, c in enumerate(cols)])
        column_names = [sg.Text(c, **attr.base_text_with_size) for c in columns] if display_columns else []

        layout = [
            [sg.Button('Filter', **attr.base_button_with_color_safety, key=self.key_filter),
             sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_clear),
             sg.Button('Reset', **attr.base_button_with_color_safety, key=self.key_reset)],
        ] + [column_names] + [
            [sg.InputText('', **attr.base_inputtext_with_size, key=self.key_inputs[i]) for i in range(len(columns))]
        ]
        layout = [sg.Frame('', layout)]
        #layout = [sg.Frame('Filter', layout, title_location=sg.TITLE_LOCATION_RIGHT)]

        self.layout = layout

    def set_window(self, window):
        self.window = window

    def handle(self, event, values):
        if event == self.key_filter:
            self.filter(values)
        elif event == self.key_clear:
            self.clear(values)
        elif event == self.key_reset:
            self.reset()

    def get_table_from_database(self):
        ret = self.dbop.execute(self.query, ignore_error=True)
        if ret.is_error:
            SP.error([f'Wrong query: {self.query}', ret.show()], do_exit=False)
            return
        rows = self.dbop.fetchall()
        return rows

    def filter(self, values):
        columns = []
        texts = []
        for k, v in values.items():
            if k in self.key_inputs and v:
                columns.append(k.split('.')[2])
                texts.append(v)
        if not columns:
            return
        idxes = [self.columns.index(c) for c in columns]
        db_data = self.get_table_from_database()
        table_data = []
        for d in db_data:
            for i, t in zip(idxes, texts):
                data = d[i] if isinstance(d[i], str) else str(d[i])
                if not re.search(f'.*{t}.*', data):
                    break
            else:
                table_data.append(d)
        if len(table_data) != len(db_data):
            self.update(table_data)
            self.window[self.key_reset].update(button_color=('red', '#f5ccff'))

    def clear(self, values):
        [self.window[k].update('') for k, v in values.items() if k in self.key_inputs and v]

    def reset(self):
        table_data = self.get_table_from_database()
        self.update(table_data)
        color = (sg.DEFAULT_BUTTON_COLOR[0], attr.color_safety)
        self.window[self.key_reset].update(button_color=color)

    def update(self, table_data):
        self.window[self.key_table].update(table_data)
