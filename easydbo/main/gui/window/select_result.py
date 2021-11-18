import os
import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class SelectResultWindow(BaseWindow):
    def __init__(self, winmgr, util, query, header, data):
        super().__init__()
        self.winmgr = winmgr
        self.util = util
        self.query = query

        length = len(header[0])

        self.prefkey = prefkey = util.make_timestamp_prefix('result')
        self.key_querybtn = f'{prefkey}querybutton'
        self.key_querytxt = f'{prefkey}querytext'
        self.key_grepbtn = f'{prefkey}grepbutton'
        self.key_grepinputtxt = f'{prefkey}grepinputtext'
        self.key_csvbtn = f'{prefkey}csvbutton'
        self.key_datatable = f'{prefkey}datatable'

        self.layout = [
            [
                sg.Button('Query', key=self.key_querybtn, **attr.base_button),
                sg.Text(query, key=self.key_querytxt, **attr.base_text),
            ],
            [
                sg.Button('Grep', key=self.key_grepbtn, **attr.base_button),
                sg.InputText('', key=self.key_grepinputtxt, **attr.base_text),
            ],
            #[
            #    sg.Button(f'SaveAsCSV', key=self.key_csvbtn, **attr.base_button),
            #    sg.InputText('', key=self.key_csvinputtext, **attr.base_inputtext),
            #],
            [
                sg.InputText(visible=False, enable_events=True, key=self.key_csvbtn),
                sg.FileSaveAs('SaveAsCSV', **attr.base_button, file_types=(('CSV', '.csv'), )),
            ],
            [
                sg.Table(
                    data,
                    headings=header,
                    justification='right',
                    selected_row_colors='red on yellow',
                    expand_x=True,
                    expand_y=True,
                    key=self.key_datatable,
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

    def get_table_data(self):
        header = self.window[self.key_datatable].ColumnHeadings
        data = self.window[self.key_datatable].get()
        return header, data

    def handle(self, event, values):
        if event == self.key_querybtn:
            from .save_as_alias import SaveAsAliasWindow
            location = self.window.CurrentLocation()
            win = SaveAsAliasWindow(self.winmgr, self.util, self.query, parent_loc=location)
            self.winmgr.add_window(win)

        elif event == self.key_grepbtn:
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
            win = SelectResultWindow(self.winmgr, self.util, grep_cmd, header, new_data)
            self.winmgr.add_window(win)

        elif event == self.key_csvbtn:
            #filename = self.window[self.key_csvinputtext].get()
            #if not filename:
            #    return
            #filename = filename if filename.endswith('.csv') else f'{filename}.csv'
            #filename = os.path.abspath(filename)
            path = values[self.key_csvbtn]
            header, data = self.get_table_data()
            with open(path, 'w') as f:
                data = self.util.to_csv(header, data)
                f.write(data)
                self.print(f'Save: {path}')
