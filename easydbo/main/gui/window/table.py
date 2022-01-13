import PySimpleGUI as sg
import re
from easydbo.exception import EASYDBO_USER_ERROR
from easydbo.output.log import Log
from .base import BaseWindow
from .candidate import CandidateWindow
from .common.command import save_table_data, execute_table_command, make_grep_command
from .common.layout.attribution import Attribution as attr
from .common.layout.filter import FilterLayout
from ..manager import SubWindow


class TableWindow(BaseWindow):
    def __init__(self, tname, pack, location):
        self.tname = tname
        self.pack = pack
        #
        self.dbop = pack.dbop
        self.columns = pack.tableop.get_columns([tname], full=True)[0]
        cfg = pack.configs.table_window
        #self.types = pack.tableop.get_types([tname])[0]
        self.sort_reverse = True
        self.rightclick_location = (-1, -1)
        #
        self.filter_windows = None
        #
        table = self.pack.tableop.get_tables(targets=[self.tname])[0]
        self.pk = table.pk
        self.pkidx = table.pkidx
        self.pkauto = table.pkauto

        #
        # Keys
        #

        prefkey = self.make_prefix_key(f'table{tname}')
        self.key_description = f'{prefkey}description'
        self.key_inputs = [f'{prefkey}{c}.input' for c in self.columns]
        self.key_candidates = [f'{prefkey}{c}.candidate.{i}' for i, c in enumerate(self.columns)]
        self.key_insert = f'{prefkey}insert'
        self.key_clear = f'{prefkey}clear'
        self.key_saveall = f'{prefkey}saveall'
        self.key_printall = f'{prefkey}printall'
        self.key_greprun = f'{prefkey}grepbtn'
        self.key_greptext = f'{prefkey}greptext'
        self.key_copypasterow = f'{prefkey}copypasterow'
        self.key_saveselected = f'{prefkey}saveselected'
        self.key_printselected = f'{prefkey}printselected'
        #self.key_shellcmd_enter = f'{self.key_greptext}.enter'  # bind
        self.key_update = f'{prefkey}update'
        self.key_delete = f'{prefkey}delete'
        self.key_table = f'{prefkey}table'
        self.key_table_rightclick = f'{self.key_table}.rightclick'  # bind
        self.key_table_doubleclick = f'{self.key_table}.doubleclick'  # bind
        #
        self.key_rightclick_cell_copypaste = '[Cell] CopyPaste'
        self.key_rightclick_cell_print = '[Cell] Print'
        self.key_rightclick_row_copypaste = '[Row] CopyPaste'
        self.key_rightclick_row_print = '[Row] Print'
        self.key_rightclick_selected_copypaste = '[Selected] CopyPaste'
        self.key_rightclick_selected_print = '[Selected] Print'
        self.key_rightclick_selected_save = '[Selected] Save'
        self.key_rightclick_all_print = '[All] Print'
        self.key_rightclick_all_save = '[All] Save'

        #
        # Layout
        #

        # layout_insert
        self._desc_col_data, text_colors = self._get_description_and_textcolor(self.dbop, self.tname, len(self.columns))
        layout_insert = [
            [sg.Text(f' {tname} ', **attr.text_table),
             sg.Button('Description', **attr.base_button_with_color_safety, key=self.key_description)],
            [sg.Text(c, **attr.base_text, key=self.key_candidates[i], size=(20, 1), enable_events=True,
                     background_color=text_colors[i]) for i, c in enumerate(self.columns)],
            [sg.InputText('', **attr.base_inputtext, key=self.key_inputs[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [sg.Button('Insert', **attr.base_button_with_color_warning, key=self.key_insert),
             sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_clear)],
        ]

        # layout_filter
        query = f'SELECT * from {tname}'
        self.filter_layout = FilterLayout(prefkey, self.columns, self.key_table, pack.dbop, query)
        layout_filter = self.filter_layout.layout

        # layout_all
        layout_all = []
        if cfg.enable_all_save:
            layout_all.append(sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_saveall))
        if cfg.enable_all_print:
            layout_all.append(sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printall))
        if cfg.enable_all_greprun:
            layout_all.append(sg.Button('GrepRun', **attr.base_button_with_color_safety, key=self.key_greprun))
            layout_all.append(sg.InputText('', **attr.base_inputtext, key=self.key_greptext))
        if layout_all:
            layout_all = [sg.Frame('All', [layout_all], title_location=sg.TITLE_LOCATION_RIGHT)]

        # layout_selected
        layout_selected = []
        if cfg.enable_selected_copypaste:
            layout_selected.append(sg.Button('CopyPaste', **attr.base_button_with_color_safety, key=self.key_copypasterow))
        if cfg.enable_selected_save:
            layout_selected.append(sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_saveselected))
        if cfg.enable_selected_print:
            layout_selected.append(sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printselected))
        layout_selected += [sg.Button('Update', **attr.base_button_with_color_warning, key=self.key_update),
                            sg.Button('Delete', **attr.base_button_with_color_danger, key=self.key_delete)]
        layout_selected = [sg.Frame('Selected', [layout_selected], title_location=sg.TITLE_LOCATION_RIGHT)],

        # layout_table
        separator_line = '-' * 30
        self.rightclick_commands = rc_cmds = []
        if cfg.enable_rightclick_cell_copypaste:
            rc_cmds.append(self.key_rightclick_cell_copypaste)
        if cfg.enable_rightclick_cell_print:
            rc_cmds.append(self.key_rightclick_cell_print)
        if cfg.enable_rightclick_cell_copypaste or cfg.enable_rightclick_cell_print:
            rc_cmds.append(separator_line)
        if cfg.enable_rightclick_row_copypaste:
            rc_cmds.append(self.key_rightclick_row_copypaste)
        if cfg.enable_rightclick_row_print:
            rc_cmds.append(self.key_rightclick_row_print)
        if cfg.enable_rightclick_row_copypaste or cfg.enable_rightclick_row_print:
            rc_cmds.append(separator_line)
        if cfg.enable_rightclick_selected_copypaste:
            rc_cmds.append(self.key_rightclick_selected_copypaste)
        if cfg.enable_rightclick_selected_print:
            rc_cmds.append(self.key_rightclick_selected_print)
        if cfg.enable_rightclick_selected_save:
            rc_cmds.append(self.key_rightclick_selected_save)
        if cfg.enable_rightclick_selected_copypaste or cfg.enable_rightclick_selected_print or cfg.enable_rightclick_selected_save:
            rc_cmds.append(separator_line)
        if cfg.enable_rightclick_all_print:
            rc_cmds.append(self.key_rightclick_all_print)
        if cfg.enable_rightclick_all_save:
            rc_cmds.append(self.key_rightclick_all_save)
        layout_table = [
            [sg.Table(
                self.get_table_from_database(),
                **attr.base_table,
                key=self.key_table,
                headings=self.columns,
                col_widths=[20 for _ in range(len(self.columns))],
                enable_click_events=True,
                right_click_menu=['&Right', rc_cmds] if rc_cmds else [],
                expand_y=True,
            )],
        ]

        layout = [
            layout_insert,
            layout_filter,
            layout_all,
            layout_selected,
            layout_table,
        ]

        #
        # Window
        #

        self._window = sg.Window(
            f'EasyDBO {tname}',
            layout,
            finalize=True,
            location=location,
            resizable=True,
            size=(1300, 1000),
        )
        # Pass widnow
        self.filter_layout.set_window(self._window)
        # Subwindows
        subwin_names = [self.key_description] + self.key_candidates + [self.key_update]
        self.subwin = SubWindow(self.window, subwin_names)

        # Table
        self.table = self.window[self.key_table]

        # Bind
        self.window[self.key_table].bind('<Button-3>', f'.{self.key_table_rightclick.split(".")[-1]}')
        self.window[self.key_table].bind('<Double-Button-1>', f'.{self.key_table_doubleclick.split(".")[-1]}')
        #self.window[self.key_greptext].bind('<Enter>', f'.{self.key_shellcmd_enter.split(".")[-1]}')  # Slow

    def _get_description_and_textcolor(self, dbop, tname, num_columns):
        # Description
        des_cols, des_data = dbop.get_description(tname)
        # Check
        colors = [None] * num_columns
        if des_cols != ['Field', 'Type', 'Null', 'Key', 'Default', 'Extra']:
            return (des_cols, des_data), colors
        # Change Null to None(NULL)
        des_cols[des_cols.index('Null')] = 'None(NULL)'
        # Convert for readability
        idx = des_cols.index('Field')
        columns = [d[idx] for d in des_data] + ['HEADER']
        data = []
        for i, c in enumerate(des_cols):
            if i == idx:
                continue
            data.append([d[i] for d in des_data] + [c])
        # Text background color
        i_null = des_cols.index('None(NULL)')  # Original is Null, not None(NULL)
        i_extra = des_cols.index('Extra')
        nulls = [d[i_null] for d in des_data]
        extra = [d[i_extra] for d in des_data]
        colors = [attr.color_optional if n == 'YES' or e.find('auto_increment') != -1 else
                  attr.color_required for n, e in zip(nulls, extra)]
        # Return
        return (columns, data), colors

    def _compare_tables(self):
        rows_gui = self.table.get()
        rows_db = self.get_table_from_database()
        if len(rows_gui) != len(rows_db):
            print(f'[PROGRAM ERROR] rows_gui({len(rows_gui)}) and rows_db({len(rows_db)}) have different line lengths')
        rows_large, rows_small, name_large, name_small = \
            (rows_db, rows_gui, 'DB', 'GUI') if len(rows_gui) < len(rows_db) else \
            (rows_gui, rows_db, 'GUI', 'DB')
        has_err = False
        for rl in rows_large[:]:
            rows_large.pop(0)
            try:
                rows_small.pop(rows_small.index(rl))
            except ValueError:
                print(f'[PROGRAM ERROR] Only {name_large} has {rl}')
                has_err = True
        for rs in rows_small:
            print(f'[PROGRAM ERROR] Only {name_small} has {rs}')
            has_err = True
        return has_err

    def close(self):
        if __debug__:
            if self._compare_tables():
                return
            print(f'[DEBUG] TableWindow "{self.tname}" finished without any problems')
        super().close()

    def get_table_from_database(self):
        query = f'SELECT * FROM {self.tname};'
        ret = self.dbop.execute(query, ignore_error=True)
        if ret.is_error:
            print(f'[Error] Something is wrong\n{ret}')
            return self.close()
        rows = self.dbop.fetchall()
        return rows

    # handle --->

    def handle(self, event, values):
        if isinstance(event, tuple):
            if event[0:2] == (self.key_table, '+CICKED+'):  # On table
                row, col = event[2]
                if row == -1:  # True when header line clicked
                    self.sort(col)
                #else:
                #    self.input_row(row - 1)
            return
        if event in self.key_description:
            self.open_table_infomation_window(event)
        elif event in self.key_candidates:
            self.open_candidate_window(event)
        elif event == self.key_insert:
            self.insert(values)
        elif event == self.key_clear:
            self.clear()
        elif event.startswith(self.filter_layout.prefkey):
            self.filter_layout.handle(event, values)
        elif event == self.key_saveall:
            self.save_as_csv(is_all=True)
        elif event == self.key_printall:
            self.print_rows(is_all=True)
        #elif event == self.key_greprun or event == self.key_shellcmd_enter:
        elif event == self.key_greprun:
            self.greprun(values[self.key_greptext])
        elif event == self.key_copypasterow:
            rows = values[self.key_table]
            if rows:
                self.copypaste_row(rows[0])
        elif event == self.key_saveselected:
            self.save_as_csv(rows=values[self.key_table])
        elif event == self.key_printselected:
            self.print_rows(rows=values[self.key_table])
        elif event == self.key_update:
            self.update(event, values)
        elif event == self.key_delete:
            self.delete(values)
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
            # Cell
            if event == self.key_rightclick_cell_copypaste:
                self.copypaste_cell(row, col)
            elif event == self.key_rightclick_cell_print:
                self.print_cell(row, col)
            # Row
            elif event == self.key_rightclick_row_copypaste:
                self.copypaste_row(row)
            elif event == self.key_rightclick_row_print:
                self.print_rows(rows=[row])
            # Selected
            elif event == self.key_rightclick_selected_copypaste:
                rows = values[self.key_table]
                if rows:
                    self.copypaste_row(rows[0])
            elif event == self.key_rightclick_selected_print:
                self.print_rows(rows=values[self.key_table])
            elif event == self.key_rightclick_selected_save:
                self.save_as_csv(rows=values[self.key_table])
            # All
            elif event == self.key_rightclick_all_print:
                self.print_rows(is_all=True)
            elif event == self.key_rightclick_all_save:
                self.save_as_csv(is_all=True)
        elif event == self.key_table_doubleclick:
            self.print_rows(rows=values[self.key_table])

    # <--- handle

    def open_table_infomation_window(self, key):
        columns, data = self._desc_col_data
        location = self.subwin.get_location(widgetkey=key, widgety=True, dy=150)
        self.subwin.create_unique(key, TableDescriptionWindow, self.pack, self.tname, columns, data, location)

    def open_candidate_window(self, key):
        idx = int(key.split('.')[-1])
        #-----------------------------------------------
        #data = [d[idx] for d in self.table_data]
        # QUESTION: Slow performance?
        query = f'SELECT DISTINCT({self.columns[idx]}) FROM {self.tname}'
        ret = self.dbop.execute(query)
        if ret.is_error:
            Log.fatal_error(f'Bad query: {query}')
        data = [d[0] for d in self.dbop.fetchall()]
        #-----------------------------------------------
        element = self.window[self.key_inputs[idx]]
        location = self.subwin.get_location(widgetkey=self.key_inputs[idx], widgetx=True, widgety=True, dy=30)
        self.subwin.create_unique(key, CandidateWindow, data, self.pack, element, location)

    def get_fields(self, primary_value):
        # FIXME: Codes should be rewritten to type conversions rather than query database
        column_str = ", ".join(self.columns)
        column_name = self.columns[self.pkidx]
        query = f'SELECT {column_str} from {self.tname} WHERE {column_name} = "{primary_value}"'
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
        table_data = self.table.get()
        table_data.insert(0, data_conv)
        self.table.update(table_data)
        print(f'[Insert] {data}')

    def clear(self):
        for k in self.key_inputs:
            self.window[k].update('')

    def copypaste_row(self, row):
        data = self.table.get()[row]
        for k, d in zip(self.key_inputs, data):
            self.window[k].update(d)

    def update(self, key, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        table_data = self.table.get()
        data = [table_data[r] for r in rows]
        location = self.subwin.get_location(widgetkey=self.key_update, widgety=True, dy=60)
        self.subwin.create_unique(key, TableUpdateWindow, self, self.pack, rows, self.tname, self.columns, data, table_data, location)

    def delete(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        # Confirm deletion
        #loc = self.subwin.get_location(widgetkey=self.key_delete, widgetx=True, widgety=True)
        #ret = sg.popup_ok_cancel('Delete selected rows?', keep_on_top=True, location=loc)
        #if ret == 'Cancel':
        #    return
        # Delete data
        table_data = self.table.get()
        data = [table_data[r] for r in rows]
        pkvals = [d[self.pkidx] for d in data]
        ret = self.dbop.delete_by_pk(self.tname, self.pk, pkvals, ignore_error=True)
        if ret.is_error:
            return
        self.dbop.commit()
        [table_data.pop(r - i) for i, r in enumerate(rows)]
        self.table.update(table_data)
        [print(f'[Delete] {list(d)}') for d in data]

    def save_as_csv(self, rows=[], is_all=False):
        if not rows and not is_all:
            return
        path = sg.popup_get_file('Save', save_as=True, no_window=True, file_types=(('CSV', '.csv'),))
        if not path:
            return
        data = self.table.get()
        if not is_all:
            data = [data[r] for r in rows]
        save_table_data(path, self.table.ColumnHeadings, data)

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

    def print_rows(self, rows=[], is_all=False):
        if not rows and not is_all:
            return
        data = self.table.get()
        if not is_all:
            data = [data[r] for r in rows]
        self.prettyrun(data=data)

    # <--- use shell command

    def sort(self, idx_column):
        table_data = self.table.get()
        table_data.sort(key=lambda k: k[idx_column], reverse=self.sort_reverse)
        self.table.update(table_data)
        self.sort_reverse = not self.sort_reverse

    def copypaste_cell(self, row, col):
        data = self.table.get()[row][col]
        self.window[self.key_inputs[col]].update(data)

    def print_cell(self, row, col):
        data = self.table.get()[row][col]
        print(data)

    # ---> Update table by external notifications

    def update_table_from_outside(self, rows, updates):
        """
        rows   : List(int)      : Row number of self.table to update
        updates: List(List(str)): Row values of self.table to update
        """
        table_data = self.table.get()
        updates_conv = [self.get_fields(u[self.pkidx]) for u in updates]
        for r, u in zip(rows, updates_conv):
            table_data[r] = u
        self.table.update(table_data)
        [print(f'[Update] {update}') for update in updates]

    # <--- Update table by external notifications


class TableDescriptionWindow(BaseWindow):
    def __init__(self, pack, tname, columns, data, location):
        layout = [
            [sg.Table(
                data,
                **attr.base_table,
                #col_widths=[20 for _ in range(len(columns))],
                enable_click_events=True,
                expand_x=True,
                expand_y=True,
                headings=columns,
                hide_vertical_scroll=True,
                justification='left',
            )],
        ]

        self._window = sg.Window(
            f'EasyDBO {tname} description',
            layout,
            finalize=True,
            grab_anywhere=True,
            keep_on_top=True,
            location=location,
            margins=(0, 0),
            no_titlebar=True,
            resizable=True,
            size=(1500, 250),
        )

    def handle(self, event, values):
        self.close()


class TableUpdateWindow(BaseWindow):
    def __init__(self, parent, pack, rows, tname, columns, selected_data, table_data, location):
        self.parent = parent
        self.pack = pack
        self.rows = rows
        self.tname = tname
        self.columns = columns
        self.selected_data = selected_data
        self.table_data = table_data
        #
        self.dbop = self.pack.dbop

        prefkey = self.make_prefix_key(f'table{tname}update')
        self.key_update = f'{prefkey}update'
        self.key_inputs = [[f'{prefkey}{r}.{c}.input' for c in columns] for r in rows]

        layout = [
            [sg.Button('Update', **attr.base_button, button_color=attr.color_warning, key=self.key_update)],
            [sg.Text(c, **attr.base_text, size=(20, 1)) for i, c in enumerate(columns)],
            [[sg.InputText(d0d, **attr.base_inputtext, key=self.key_inputs[i][j], size=(20, 1))
              for j, d0d in enumerate(d1d)] for i, d1d in enumerate(selected_data)],
        ]

        self._window = sg.Window(
            f'EasyDBO {tname} Update',
            layout,
            finalize=True,
            keep_on_top=True,
            location=location,
            modal=True,
            resizable=True,
            size=(1300, 400),
        )

    def handle(self, event, values):
        if event == self.key_update:
            self.update()

    def update(self):
        # Check
        try:
            if not all([self.selected_data[i] == self.table_data[r] for i, r in enumerate(self.rows)]):
                raise EASYDBO_USER_ERROR
        except (EASYDBO_USER_ERROR, IndexError):
            print('Error: Cannot update because table has been changed')
            self.close()
            return

        table = self.pack.tableop.get_tables(targets=[self.tname])[0]
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
        self.parent.update_table_from_outside(rows, updates)
        self.close()
