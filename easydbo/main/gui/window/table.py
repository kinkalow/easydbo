import PySimpleGUI as sg
import re
from .filter import FilterWindow
from .base import BaseWindow
from .layout.common import Attribution as attr
from .command.common import save_table_data, execute_table_command, make_grep_command
from easydbo.output.log import Log

class TableWindow(BaseWindow):
    def __init__(self, tname, util, location):
        super().__init__(util.winmgr)

        self.tname = tname
        self.util = util
        #
        self.dbop = util.dbop
        self.columns = util.tableop.get_columns([tname], full=True)[0]
        #self.types = util.tableop.get_types([tname])[0]
        self.sort_reverse = True
        self.rightclick_location = (-1, -1)
        #
        self.filter_windows = None
        self.candidate_windows = [None] * len(self.columns)
        #
        table = self.util.tableop.get_tables(targets=[self.tname])[0]
        self.pk = table.pk
        self.pkidx = table.pkidx
        self.pkauto = table.pkauto

        self.prefkey = prefkey = f'_table{tname}__.'
        #self.key_columns = [f'{prefkey}{c}' for c in self.columns]
        self.key_inputs = [f'{prefkey}{c}.input' for c in self.columns]
        self.key_candidates = [f'{prefkey}{c}.candidate.{i}' for i, c in enumerate(self.columns)]
        self.key_insert = f'{prefkey}insert'
        self.key_clear = f'{prefkey}reset'
        self.key_save = f'{prefkey}save'
        self.key_printall = f'{prefkey}printall'
        self.key_filter = f'{prefkey}filter'
        self.key_greprun = f'{prefkey}grepbtn'
        self.key_greptext = f'{prefkey}greptext'
        self.key_copypaste = f'{prefkey}copypaste'
        self.key_printselect = f'{prefkey}printselect'
        #self.key_shellcmd_enter = f'{self.key_greptext}.enter'  # bind
        self.key_update = f'{prefkey}update'
        self.key_delete = f'{prefkey}delete'
        self.key_table = f'{prefkey}table'
        self.key_table_rightclick = f'{self.key_table}.rightclick'  # bind
        self.key_table_doubleclick = f'{self.key_table}.doubleclick'  # bind
        #
        self.key_rightclick_copypastecell = 'CopyPasteCell'
        self.key_rightclick_printcell = 'PrintCell'

        self.rightclick_commands = [self.key_rightclick_copypastecell, self.key_rightclick_printcell]
        layout = [
            [sg.Text(f' {tname} ', **attr.text_table)],
            [sg.Text(c, **attr.base_text, key=self.key_candidates[i], size=(20, 1), enable_events=True, background_color='#79799c') for i, c in enumerate(self.columns)],
            [sg.InputText('', **attr.base_inputtext, key=self.key_inputs[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [
                sg.Button('Insert', **attr.base_button_with_color_warning, key=self.key_insert),
                sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_clear),
            ],
            [sg.Text()],
            [
                sg.Frame('All', [
                    [
                        sg.InputText(**attr.base_inputtext, key=self.key_save, visible=False, enable_events=True),
                        sg.FileSaveAs('Save', **attr.base_button_with_color_safety, file_types=(('CSV', '.csv'), )),
                        sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printall),
                        sg.Button('Filter', **attr.base_button_with_color_safety, key=self.key_filter),
                        sg.Button('GrepRun', **attr.base_button_with_color_warning, key=self.key_greprun),
                        sg.InputText('', **attr.base_inputtext, key=self.key_greptext),
                    ]
                ],
                title_location=sg.TITLE_LOCATION_RIGHT,
                )
            ],
            [
                sg.Frame('Selected', [[
                    sg.Button('CopyPaste', **attr.base_button_with_color_safety, key=self.key_copypaste),
                    sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printselect),
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
            size=(1300, 800),
            resizable=True,
            finalize=True,
            location=location,
        )

        # Table
        self.table = self.window[self.key_table]
        self.table_data = self._show_table_data()

        # Bind
        self.window[self.key_table].bind('<Button-3>', f'.{self.key_table_rightclick.split(".")[-1]}')
        self.window[self.key_table].bind('<Double-Button-1>', f'.{self.key_table_doubleclick.split(".")[-1]}')
        #self.window[self.key_greptext].bind('<Enter>', f'.{self.key_shellcmd_enter.split(".")[-1]}')  # Slow

    def _show_table_data(self):
        query = f'SELECT * FROM {self.tname};'
        ret = self.dbop.execute(query, ignore_error=True)
        if ret.is_error:
            print(f'[Error] Something is wrong\n{ret}')
            return self.close()
        rows = self.dbop.fetchall()
        self.table.update(rows)
        return rows

    # handle --->

    def handle(self, event, values):
        if event in self.key_candidates:
            idx = int(event.split('.')[-1])
            self.open_candidate_window(idx)
        elif event == self.key_insert:
            self.insert(values)
        elif event == self.key_clear:
            self.clear()
        elif event == self.key_save:
            path = values[self.key_save]
            self.save_as_csv(path)
        elif event == self.key_printall:
            self.print_table_data(is_all=True)
        #elif event == self.key_greprun or event == self.key_shellcmd_enter:
        elif event == self.key_greprun:
            self.greprun(values[self.key_greptext])
        elif event == self.key_copypaste:
            self.copypaste(values)
        elif event == self.key_printselect:
            self.print_table_data(rows=values[self.key_table])
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
            if row == -1:  # Ignore header line
                return
            if event == self.key_rightclick_copypastecell:
                self.copypaste_cell(row, col)
            elif event == self.key_rightclick_printcell:
                self.print_cell(row, col)
        elif event == self.key_table_doubleclick:
            self.print_table_data(rows=values[self.key_table])

    def open_candidate_window(self, idx):
        if self.candidate_windows[idx] in self.util.winmgr.windows:
            return
        from .candidate import CandidateWindow
        data = [d[idx] for d in self.table_data]
        element = self.window[self.key_inputs[idx]]
        location = self.get_location(widgetkey=self.key_inputs[idx], widgetx=True, widgety=True, dy=30)
        win = CandidateWindow(data, self.util, element, location)
        self.util.winmgr.add_window(win)
        self.candidate_windows[idx] = win.get_window()

    def get_fields(self, primary_value):
        # FIXME: Codes should be rewritten to type conversions rather than query database
        column_str = ", ".join(self.columns)
        column_name = self.columns[self.pkidx]
        query = f'SELECT {column_str} from {self.tname} WHERE {column_name} = {primary_value}'
        ret = self.dbop.execute(query)
        if ret.is_error:
            Log.fatal_error(f'Bad querry: {query}')
        return self.dbop.fetchall()[0]

    def to_mysql(self, data):
        """
        data: List(any)
        """
        if self.pkauto and not data[self.pkidx]:
            data[self.pkidx] = self.dbop.get_autoincrement(self.tname, self.pk)
        data = [None if not d else d if isinstance(d, str) else str(d) for d in data]
        return data

    def insert(self, values):
        data = [self.window[k].get() for k in self.key_inputs]
        data = self.to_mysql(data)
        ret = self.dbop.insert(self.tname, self.columns, [data], ignore_error=True)
        if ret.is_error:
            return
        self.dbop.commit()
        data_conv = self.get_fields(data[self.pkidx])
        self.table_data.insert(0, data_conv)
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

    def filter(self, values):
        if self.filter_windows in self.util.winmgr.windows:
            return
        location = self.get_location(widgetkey=self.key_filter, widgety=True, dy=60)
        win = FilterWindow(self.tname, self.columns, self.table_data, self.util, location)
        self.util.winmgr.add_window(win)
        self.filter_windows = win.get_window()

    def update(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        data = [self.table_data[r] for r in rows]
        location = self.get_location(widgetkey=self.key_update, widgety=True, dy=60)
        winobj = TableUpdateWindow(self, self.util, rows, self.tname, self.columns, data, self.table_data, location)
        self.util.winmgr.add_window(winobj)

    def notify_update(self, rows, updates):
        """
        rows   : List(int)      : Row number of self.table to update
        updates: List(List(str)): Row values of self.table to update
        """
        updates_conv = [self.get_fields(u[self.pkidx]) for u in updates]
        for r, u in zip(rows, updates_conv):
            self.table_data[r] = u
        self.table.update(self.table_data)
        [print(f'[Update] {update}') for update in updates]

    def delete(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        # Confirm deletion
        #loc = self.get_location(widgetkey=self.key_delete, widgetx=True, widgety=True)
        #ret = sg.popup_ok_cancel('Delete selected rows?', keep_on_top=True, location=loc)
        #if ret == 'Cancel':
        #    return
        # Delete data
        data = [self.table_data[r] for r in rows]
        pkvals = [d[self.pkidx] for d in data]
        ret = self.dbop.delete_by_pk(self.tname, self.pk, pkvals, ignore_error=True)
        if ret.is_error:
            return
        self.dbop.commit()
        [self.table_data.pop(r - i) for i, r in enumerate(rows)]
        self.table.update(self.table_data)
        [print(f'[Delete] {list(d)}') for d in data]

    def save_as_csv(self, path):
        save_table_data(path, self.table.ColumnHeadings, self.table.get())

    # ---> use shell command

    def _get_columns_data(self, columns, data):
        columns = columns if columns else self.table.ColumnHeadings
        data = data if data != [[]] else self.table.get()
        return columns, data

    def greprun(self, patten, columns=[], data=[[]], delimiter=',', show_command=True):
        patten = make_grep_command(patten)
        if not patten or re.search(r'>', patten):  # Prevent redirection
            return
        columns, data = self._get_columns_data(columns, data)
        cmd = f'column -t -s {delimiter} {{path}} | {patten}'
        execute_table_command(cmd, columns, data, delimiter, show_command)

    def prettyrun(self, columns=[], data=[[]], delimiter=',', show_command=False):
        columns, data = self._get_columns_data(columns, data)
        cmd = f'column -t -s {delimiter} {{path}}'
        execute_table_command(cmd, columns, data, delimiter, show_command)

    def print_table_data(self, rows=[], is_all=False):
        if not rows and not is_all:
            return
        data = [self.table_data[r] for r in rows] if rows else self.table_data
        self.prettyrun(data=data)

    # <--- use shell command

    def sort(self, idx_column):
        self.table_data.sort(key=lambda k: k[idx_column], reverse=self.sort_reverse)
        self.table.update(self.table_data)
        self.sort_reverse = not self.sort_reverse

    def copypaste_cell(self, row, col):
        data = self.table_data[row][col]
        self.window[self.key_inputs[col]].update(data)

    def print_cell(self, row, col):
        data = self.table.get()[row][col]
        print(data)

    # <--- handle


class TableUpdateWindow(BaseWindow):
    def __init__(self, parent, util, rows, tname, columns, selected_data, table_data, location):
        super().__init__(util.winmgr)

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
            size=(1300, 400),
            resizable=True,
            finalize=True,
            location=location,
        )

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

        rows = []
        updates = []
        for i, (row, keys) in enumerate(zip(self.rows, self.key_inputs)):
            origin = self.selected_data[i]
            origin = self.parent.to_mysql(origin)
            update = [self.window[k].get() for k in keys]  # window[k].get() returns str because it calls tkinter.StringVar
            update = self.parent.to_mysql(update)
            diff = {c: u for i, (c, o, u) in enumerate(zip(self.columns, origin, update)) if o != u}
            if not diff:
                continue
            pkval = origin[pkidx]
            ret = self.dbop.update(self.tname, diff, pk, pkval, ignore_error=True)
            if ret.is_error:
                return self.dbop.rollback()
            rows.append(row)
            updates.append(update)

        self.dbop.commit()
        self.parent.notify_update(rows, updates)
        self.close()
