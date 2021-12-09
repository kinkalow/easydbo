#import os
import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class QueryResultWindow(BaseWindow):
    def __init__(self, util, query, header, data, location, use_query_btn=True):
        super().__init__(util.winmgr)

        self.util = util
        self.query = query

        length = len(header[0])

        self.prefkey = prefkey = util.make_timestamp_prefix('result')
        self.key_querybtn = f'{prefkey}querybutton'
        self.key_querytxt = f'{prefkey}querytext'
        self.key_grepbtn = f'{prefkey}grepbutton'
        self.key_grepinputtxt = f'{prefkey}grepinputtext'
        self.key_save = f'{prefkey}csvbutton'
        self.key_table = f'{prefkey}table'

        if use_query_btn:
            query_btn = [
                sg.Button('Query', **attr.base_button_with_color_safety, key=self.key_querybtn),
                sg.Text(query, **attr.base_text, key=self.key_querytxt),
            ]
        else:
            query_btn = []
        self.layout = [query_btn] + [
            [
                sg.Button('Grep', **attr.base_button_with_color_safety, key=self.key_grepbtn),
                sg.InputText('', **attr.base_text, key=self.key_grepinputtxt),
            ],
            #[
            #    sg.Button(f'SaveAsCSV', key=self.key_save, **attr.base_button),
            #    sg.InputText('', key=self.key_csvinputtext, **attr.base_inputtext),
            #],
            [
                sg.InputText(**attr.base_inputtext, key=self.key_save, visible=False, enable_events=True),
                sg.FileSaveAs('Save', **attr.base_button_with_color_safety, file_types=(('CSV', '.csv'), )),
            ],
            [
                sg.Table(
                    data,
                    **attr.base_table,
                    key=self.key_table,
                    headings=header,
                    col_widths=[20 for _ in range(length)],
                    expand_y=True,
                )
            ],
        ]

        self.window = sg.Window(
            'EasyDBO QueryResult',
            self.layout,
            location=location,
            size=(1300, 800),
            resizable=True,
            finalize=True,
        )

    def get_table_data(self):
        header = self.window[self.key_table].ColumnHeadings
        data = self.window[self.key_table].get()
        return header, data

    def handle(self, event, values):
        if event == self.key_querybtn:
            self.add_alias()
        elif event == self.key_grepbtn:
            self.grep()
        elif event == self.key_save:
            path = values[self.key_save]
            self.save_as_csv(path)

    def add_alias(self):
        from .save_as_alias import SaveAsAliasWindow
        location = self.get_location(dy=30)
        win = SaveAsAliasWindow(self.util, self.query, location)
        self.winmgr.add_window(win)

    def grep(self):
        grep_pat = self.window[self.key_grepinputtxt].get()
        if not grep_pat:
            return
        header, data = self.get_table_data()
        data_sp = self.util.to_csv([], data, delimiter=' ')
        new_data = []
        try:
            import tempfile
            fp = tempfile.NamedTemporaryFile(mode='w')
            fp.write(data_sp)
            fp.seek(0)
            path = fp.name
            import subprocess
            grep_cmd = f'grep -ne "{grep_pat}" {path} | sed -e "s/:.*//g"'
            p = subprocess.Popen(grep_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            out = p.communicate()[0]
            grep_num = out.decode().rstrip('\n').split('\n')
            if grep_num == ['']:
                self.print(f'No matching patten: {grep_pat}')
                return
            new_data = [data[int(i) - 1] for i in grep_num]
        except Exception as e:
            self.print(e)
            fp.close()
            return
        if data == new_data:
            self.print(f'All data matched for patten: {grep_pat}')
            return
        # Show grep result on new window
        win = QueryResultWindow(self.winmgr, self.util, grep_cmd, header, new_data, use_query_btn=False)
        self.winmgr.add_window(win)

    def save_as_csv(self, path):
        from .command.common import save_table_data
        table = self.window[self.key_table]
        save_table_data(path, table.ColumnHeadings, table.get())
