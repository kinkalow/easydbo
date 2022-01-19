import PySimpleGUI as sg
from easydbo.output.print_ import SimplePrint as SP
from .base import BaseWindow
from .common.layout.attribution import Attribution as attr
from .common.layout.filter import FilterLayout
from ..manager import SubWindow

class QueryResultWindow(BaseWindow):
    def __init__(self, pack, query, columns, table_data, location, use_query_btn=True):
        self.pack = pack
        self.query = query
        self.table_data = table_data

        length = len(columns[0])

        self.prefkey = prefkey = self.make_prefix_key('result', timestamp=True)
        self.key_querybtn = f'{prefkey}querybutton'
        self.key_querytxt = f'{prefkey}querytext'
        self.key_grepbtn = f'{prefkey}grepbutton'
        self.key_grepinputtxt = f'{prefkey}grepinputtext'
        self.key_save = f'{prefkey}csvbutton'
        self.key_table = f'{prefkey}table'

        self.filter_layout = FilterLayout(prefkey, columns, self.key_table, pack.dbop, self.query, display_columns=True)

        if use_query_btn:
            query_btn = [
                sg.Button('Query', **attr.base_button_with_color_safety, key=self.key_querybtn),
                sg.Text(query, **attr.base_text, key=self.key_querytxt),
            ]
        else:
            query_btn = []
        self.layout = [query_btn] + [
            self.filter_layout.layout,
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
                    table_data,
                    **attr.base_table,
                    key=self.key_table,
                    headings=columns,
                    col_widths=[20 for _ in range(length)],
                    expand_y=True,
                )
            ],
        ]

        self._window = sg.Window(
            'EasyDBO QueryResult',
            self.layout,
            finalize=True,
            location=location,
            resizable=True,
            size=(1300, 800),
        )
        # Pass widnow
        self.filter_layout.set_window(self._window)
        # Subwindows
        self.subwin = SubWindow(self.window, [self.key_querybtn])

        #frame_id = self.window[self.key_table].Widget.frame_id
        #canvas = self.window[self.key_table].Widget.canvas
        #canvas.bind('<Configure>', lambda event, canvas=canvas, frame_id=frame_id:
        #            canvas.itemconfig(frame_id, width=canvas.winfo_width()))

    def get_table_data(self):
        columns = self.window[self.key_table].ColumnHeadings
        data = self.window[self.key_table].get()
        return columns, data

    def handle(self, event, values):
        if event == self.key_querybtn:
            self.add_alias(event)
        elif event.startswith(self.filter_layout.prefkey):
            self.filter_layout.handle(event, values)
        elif event == self.key_grepbtn:
            self.grep()
        elif event == self.key_save:
            path = values[self.key_save]
            self.save_as_csv(path)

    def add_alias(self, key):
        location = self.subwin.get_location(widgetkey=key, widgety=True, dy=60)
        self.subwin.create_unique(key, QuerySaveWindow, self.pack, self.query, location)

    def _to_csv(self, header, data2d, delimiter=','):
        header_csv = delimiter.join(header)
        data_csv = '\n'.join([delimiter.join(str(d1)) for d1 in data2d])
        data_csv = f'{data_csv}\n' if data_csv else data_csv
        return f'{header_csv}\n{data_csv}' if header else data_csv

    def grep(self):
        grep_pat = self.window[self.key_grepinputtxt].get()
        if not grep_pat:
            return
        columns, data = self.get_table_data()
        data_sp = self._to_csv([], data, delimiter=' ')
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
                SP.info(f'No matching patten: {grep_pat}')
                return
            new_data = [data[int(i) - 1] for i in grep_num]
        except Exception as e:
            SP.error(e)
            fp.close()
            return
        if data == new_data:
            SP.info(f'All data matched for patten: {grep_pat}')
            return
        # Show grep result on new window
        location = self.subwin.get_location()
        self.subwin.create_multiples(QueryResultWindow, self.pack, grep_cmd, columns, new_data, location, use_query_btn=False)

    def save_as_csv(self, path):
        from .common.command import save_table_data
        table = self.window[self.key_table]
        save_table_data(path, table.ColumnHeadings, table.get())


class QuerySaveWindow(BaseWindow):
    def __init__(self, pack, query, location):
        self.aliasmgr = pack.aliasmgr

        prefkey = self.make_prefix_key('saveasalias', timestamp=True)
        self.key_save = f'{prefkey}save'
        self.key_cancel = f'{prefkey}cancel'
        self.key_alias = f'{prefkey}alias'
        self.key_query = f'{prefkey}query'

        self.layout = [
            [
                sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_save),
                sg.Button('Close', **attr.base_button_with_color_safety, key=self.key_cancel),
            ],
            [
                sg.Text('Alias', **attr.base_text, size=(5, 1)),
                sg.InputText('', **attr.base_inputtext, key=self.key_alias),
            ],
            [
                sg.Text('Query', **attr.base_text, size=(5, 1)),
                sg.Multiline(query, **attr.base_multiline, key=self.key_query, expand_x=True, expand_y=True, size=(1300, 500)),
            ],
        ]

        self._window = sg.Window(
            'EasyDBO QuerySave',
            self.layout,
            finalize=True,
            location=location,
            resizable=True,
            size=(1300, 500),
        )

        self.subwin = SubWindow(self.window, [self.key_save])

    def handle(self, event, values):
        if event == self.key_save:
            self.save(event)
        elif event == self.key_cancel:
            self.cancel()

    def save(self, key):
        name = self.window[self.key_alias].get()
        if name == '':
            return SP.miss('Set alias name')
        # Check
        idx_update = self.aliasmgr.index(name)
        if idx_update != -1:
            loc = self.subwin.get_location(widgetkey=key, widgetx=True, widgety=True)
            ret = sg.popup_ok_cancel('Overwrite alias?', keep_on_top=True, location=loc)
            if ret == 'Cancel':
                return
        # Add or Update
        query = self.window[self.key_query].get()
        if idx_update == -1:
            self.aliasmgr.insert(0, name, query)
            add_or_update = 'Add'
        else:
            self.aliasmgr.update(name, query, index=idx_update)
            add_or_update = 'Update'
        # Update file
        self.aliasmgr.save()
        SP.info(f'{add_or_update} alias: {name}')
        self.close()

    def add(self, name, sql):
        pass

    def cancel(self):
        self.close()
