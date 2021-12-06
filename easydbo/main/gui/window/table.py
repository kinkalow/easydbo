import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class TableWindow(BaseWindow):
    def __init__(self, tname, util, parent_loc, on_close=None):
        self.tname = tname
        self.util = util
        #
        self.dbop = util.dbop
        self.columns = util.get_column(tname)
        self.on_close = on_close
        self.sort_reverse = True
        self.rightclick_location = (-1, -1)

        self.prefkey = prefkey = f'_table{tname}__.'
        self.key_tname = f'{prefkey}{tname}'
        self.key_columns = [f'{prefkey}{c}' for c in self.columns]
        self.key_inputs = [f'{prefkey}{c}.input' for c in self.columns]
        self.key_insert = f'{prefkey}insert'
        self.key_clear = f'{prefkey}reset'
        self.key_copypaste = f'{prefkey}copypaste'
        self.key_print = f'{prefkey}print'
        self.key_save = f'{prefkey}save'
        self.key_shellrun = f'{prefkey}shellrun'
        self.key_shellcmd = f'{prefkey}shellcmd'
        #self.key_shellcmd_enter = f'{self.key_shellcmd}.enter'  # bind
        self.key_filter = f'{prefkey}filter'
        self.key_update = f'{prefkey}update'
        self.key_delete = f'{prefkey}delete'
        self.key_table = f'{prefkey}table'
        self.key_table_rightclick = f'{self.key_table}.rightclick'  # bind
        #
        self.key_rightclick_copypastecell = 'CopyPasteCell'

        self.rightclick_commands = [self.key_rightclick_copypastecell]
        layout = [
            [sg.Text(f' {tname} ', **attr.text_table, key=self.key_tname)],
            [sg.Text(c, **attr.base_text, key=self.key_columns[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [sg.InputText('', **attr.base_inputtext, key=self.key_inputs[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [
                sg.Button('Insert', **attr.base_button_with_color_warning, key=self.key_insert),
                sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_clear),
            ],
            [sg.Text()],
            [
                sg.Frame('All', [
                    [
                        sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_print),
                        sg.InputText(**attr.base_inputtext, key=self.key_save, visible=False, enable_events=True),
                        sg.FileSaveAs('Save', **attr.base_button_with_color_safety, file_types=(('CSV', '.csv'), )),
                        sg.Button('Filter', **attr.base_button_with_color_safety, key=self.key_filter),
                    ],
                    [
                        sg.Button('Run', **attr.base_button_with_color_warning, key=self.key_shellrun),
                        sg.InputText('', **attr.base_inputtext, key=self.key_shellcmd),
                    ]
                ],
                title_location=sg.TITLE_LOCATION_RIGHT,
                )
            ],
            [
                sg.Frame('Selected', [[
                    sg.Button('CopyPaste', **attr.base_button_with_color_safety, key=self.key_copypaste),
                    sg.Button('Update', **attr.base_button_with_color_warning, key=self.key_update),
                    sg.Button('Delete', **attr.base_button_with_color_danger, key=self.key_delete),
                ]],
                title_location=sg.TITLE_LOCATION_RIGHT,
                )
            ],
            [sg.Table(
                [['' for _ in range(len(self.columns))]],
                **attr.base_table,
                key=self.key_table,
                headings=self.columns,
                col_widths=[20 for _ in range(len(self.columns))],
                enable_click_events=True,
                right_click_menu=['&Right', self.rightclick_commands],
                expand_y=True,
            )],
        ]

        self.window = sg.Window(
            f'EasyDBO {tname}',
            layout,
            size=(1200, 800),
            resizable=True,
            finalize=True,
            location=(30, 30),
        )
        self.window.move(parent_loc[0], parent_loc[1] + 30)

        # Table
        self.table = self.window[self.key_table]
        self.table_data = self._show_table_data()

        # Bind
        self.window[self.key_table].bind('<Button-3>', f'.{self.key_table_rightclick.split(".")[-1]}')
        #self.window[self.key_shellcmd].bind('<Enter>', f'.{self.key_shellcmd_enter.split(".")[-1]}')  # Slow

    def _show_table_data(self):
        query = f'SELECT * FROM {self.tname};'
        ret = self.dbop.execute(query, ignore_error=True)
        if ret.is_error:
            print(f'[Error] Something is wrong\n{ret}')
            return self.close()
        rows = self.dbop.fetchall()
        self.table.update(rows)
        return rows

    def close(self):
        self.window.close()
        self.window = None
        self.util.call(self.on_close)

    # handle --->

    def handle(self, event, values):
        if event == self.key_insert:
            self.insert(values)
        elif event == self.key_clear:
            self.clear()
        elif event == self.key_print:
            self.print_table_data()
        elif event == self.key_save:
            path = values[self.key_save]
            self.save_as_csv(path)
        #elif event == self.key_shellrun or event == self.key_shellcmd_enter:
        elif event == self.key_shellrun:
            self.shellrun(values[self.key_shellcmd])
        elif event == self.key_copypaste:
            self.copypaste(values)
        elif event == self.key_filter:
            self.filter(values)
        elif event == self.key_update:
            self.update(values)
        elif event == self.key_delete:
            self.delete(values)
        elif (isinstance(event, tuple) and event[0:2] == (self.key_table, '+CICKED+')):  # On table
            row, col = event[2]
            if row == -1:  # True when header line clicked
                self.sort(col)
            #else:
            #    self.input_row(row - 1)
        elif event == self.key_table_rightclick:
            e = self.table.user_bind_event
            region = self.table.Widget.identify_region(e.x, e.y)
            if region == 'heading' or region == 'cell':
                # row and col starts from 1
                # row = 0 means header line
                row = self.table.Widget.identify_row(e.y)
                row = int(row) if row else 0
                col = int(self.table.Widget.identify_column(e.x).replace('#', ''))
                self.rightclick_location = (row, col)
            else:
                self.rightclick_location = (-1, -1)
        elif event in self.rightclick_commands:
            if self.rightclick_location == (-1, -1):
                return
            row, col = self.rightclick_location[0] - 1, self.rightclick_location[1] - 1
            if event == self.key_rightclick_copypastecell:
                if row == -1:
                    return
                else:
                    self.copypaste_cell(row, col)

    def insert(self, values):
        data = [str(self.window[k].get()) for k in self.key_inputs]
        if all([True if d else False for d in data]) is False:
            return
        ret = self.dbop.insert(self.tname, self.columns, [data], ignore_error=True)
        if ret.is_error:
            return
        self.dbop.commit()
        self.table_data.insert(0, data)
        self.table.update(self.table_data)
        print(f'[Insert] {data}')

    def clear(self):
        for k in self.key_inputs:
            self.window[k].update('')

    def copypaste(self, values):
        idx_selected_rows = values[self.key_table]
        if not idx_selected_rows:
            return
        data = self.table_data[idx_selected_rows[0]]
        for k, d in zip(self.key_inputs, data):
            self.window[k].update(d)

    def copypaste_cell(self, row, col):
        data = self.table_data[row][col]
        self.window[self.key_inputs[col]].update(data)

    def get_table_data(self, rows):
        return [self.table_data[r] for r in rows]

    def filter(self, values):
        from .filter import FilterWindow
        location = self.window.CurrentLocation()
        win = FilterWindow(self.tname, self.columns, self.table_data, self.util, location)
        self.util.winmgr.add_window(win)

    def update(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        data = self.get_table_data(rows)
        location = self.window.CurrentLocation()
        winobj = TableUpdateWindow(self, self.util, rows, self.tname, self.columns, data, self.table_data, location)
        self.util.winmgr.add_window(winobj)

    def notify_update(self, rows, updates):
        for r, u in zip(rows, updates):
            self.table_data[r] = u
        self.table.update(self.table_data)
        [print(f'[Update] {update}') for update in updates]

    def delete(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        # Confirm deletion
        #loc = self.get_widget_location(self.key_delete)
        #ret = sg.popup_ok_cancel('Delete selected rows?', keep_on_top=True, location=loc)
        #if ret == 'Cancel':
        #    return
        # Delete data
        data = self.get_table_data(rows)
        table = self.util.tableop.get_tables(targets=[self.tname])[0]
        pk, pkidx = table.pk, table.pkidx
        pkvals = [d[pkidx] if isinstance(d[pkidx], str) else f'"{d[pkidx]}"' for d in data]
        ret = self.dbop.delete_by_pk(self.tname, pk, pkvals, ignore_error=True)
        if ret.is_error:
            return
        self.dbop.commit()
        [self.table_data.pop(r - i) for i, r in enumerate(rows)]
        self.table.update(self.table_data)
        [print(f'[Delete] {list(d)}') for d in data]

    def print_table_data(self):
        from .command.common import print_table_data
        data = self.table.get()
        print_table_data(data)

    def save_as_csv(self, path):
        from .command.common import save_table_data_as_csv
        save_table_data_as_csv(self.table, path)

    def shellrun(self, cmd):
        import tempfile
        import subprocess
        from .command.common import save_table_data_as_csv
        fp = tempfile.NamedTemporaryFile(mode='w+')
        path = fp.name
        save_table_data_as_csv(self.table, path, show_save_message=False)
        if not cmd:
            cmd = f'column -t -s , {path}'
        elif cmd.startswith('-'):
            cmd = f'{cmd[1:]}'.replace('<f>', path)
        else:
            cmd = f'column -t -s , {path} | {cmd}'
        print(f'[Command] {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = p.communicate()
        out, err = out.decode(), err.decode()
        if out != '':
            print(out)
        if err != '':
            print(err)
        fp.close()

    def sort(self, idx_column):
        self.table_data.sort(key=lambda k: k[idx_column], reverse=self.sort_reverse)
        self.table.update(self.table_data)
        self.sort_reverse = not self.sort_reverse

    #def input_row(self, row):
    #    print(self.table_data[row])

    # <--- handle


class TableUpdateWindow(BaseWindow):
    def __init__(self, parent, util, rows, tname, columns, selected_data, table_data, parent_loc):
        self.parent = parent
        self.util = util
        self.rows = rows
        self.tname = tname
        self.columns = columns
        self.selected_data = selected_data
        self.table_data = table_data
        #
        self.dbop = self.util.dbop

        self.prefkey = prefkey = f'_table{tname}change__.'
        self.key_update = f'{prefkey}update'
        self.key_inputs = [[f'{prefkey}{r}.{c}.input' for c in columns] for r in rows]

        layout = [
            [sg.Button('Update', **attr.base_button, button_color=attr.color_warning, key=self.key_update)],
            [sg.Text(c, **attr.base_text, size=(20, 1)) for i, c in enumerate(columns)],
            [[sg.InputText(d0d, **attr.base_inputtext, key=self.key_inputs[i][j], size=(20, 1))
              for j, d0d in enumerate(d1d)] for i, d1d in enumerate(selected_data)],
        ]

        self.window = sg.Window(
            f'EasyDBO {tname} Update',
            layout,
            size=(1200, 400),
            resizable=True,
            finalize=True,
        )
        self.window.move(parent_loc[0], parent_loc[1] + 30)

    def handle(self, event, values):
        if event == self.key_update:
            self.update()

    def update(self):
        # Check
        if not all([self.selected_data[i] == self.table_data[r] for i, r in enumerate(self.rows)]):
            print('Error: Could not update due to data changes in table')
            self.close()
            return

        table = self.util.tableop.get_tables(targets=[self.tname])[0]
        pk, pkidx = table.pk, table.pkidx

        updates = []
        for i, keys in enumerate(self.key_inputs):
            origin = self.selected_data[i]
            update = [self.window[k].get() for k in keys]
            diff = {c: u for i, (c, o, u) in enumerate(zip(self.columns, origin, update)) if o != u}
            if not diff:
                continue
            pkval = origin[pkidx]
            ret = self.dbop.update(self.tname, diff, pk, pkval, ignore_error=True)
            if ret.is_error:
                return self.dbop.rollback()
            updates.append(update)

        self.dbop.commit()
        self.parent.notify_update(self.rows, updates)
        self.close()
