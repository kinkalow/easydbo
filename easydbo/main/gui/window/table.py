import PySimpleGUI as sg
from easydbo.exception import EASYDBO_USER_ERROR
from easydbo.output.print_ import SimplePrint as SP
from .base import BaseWindow
from .candidate import CandidateWindow
from .common.layout.attribution import Attribution as attr
from .common.layout.filter import FilterLayout
from .common.layout.table import TableAllLayout, TableSelectedLayout, TableRightClick, TableClick, TableDoubleClick
from .common.popup import popup_error
from .common.util import get_location
from ..manager import SubWindow


class TableWindow(BaseWindow):
    def __init__(self, tname, pack, location):
        self.tname = tname
        self.pack = pack
        #
        self.dbop = pack.dbop
        self.columns = pack.tableop.get_columns([tname], full=True)[0]
        self.cfg = cfg = pack.configs.table_window
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
        self.key_update = f'{prefkey}update'
        self.key_delete = f'{prefkey}delete'
        self.key_table = f'{prefkey}table'

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

        # layout_table_all
        self.table_all_layout = TableAllLayout(
            prefkey, enable_save=cfg.enable_all_save,
            enable_print=cfg.enable_all_print, enable_greprun=cfg.enable_all_greprun)
        layout_table_all = self.table_all_layout.layout

        # layout_table_selected
        self.table_selected_layout = TableSelectedLayout(
            prefkey, self.key_table, enable_copypaste=cfg.enable_selected_copypaste,
            enable_save=cfg.enable_selected_save, enable_print=cfg.enable_selected_print, enable_frame=False)
        layout_table_selected = self.table_selected_layout.layout
        layout_table_selected += [sg.Button('Update', **attr.base_button_with_color_warning, key=self.key_update),
                                  sg.Button('Delete', **attr.base_button_with_color_danger, key=self.key_delete)]
        layout_table_selected = [sg.Frame('Selected', [layout_table_selected], title_location=sg.TITLE_LOCATION_RIGHT)],

        # layout_table
        self.table_rightclick = TableRightClick(
            self.key_table,
            enable_cell_copypaste=cfg.enable_rightclick_cell_copypaste, enable_cell_print=cfg.enable_rightclick_cell_print,
            enable_row_copypaste=cfg.enable_rightclick_row_copypaste, enable_row_print=cfg.enable_rightclick_row_print,
            enable_selected_copypaste=cfg.enable_rightclick_selected_copypaste, enable_selected_print=cfg.enable_rightclick_selected_print, enable_selected_save=cfg.enable_rightclick_selected_save,
            enable_all_print=cfg.enable_rightclick_all_print, enable_all_save=cfg.enable_rightclick_all_save)
        menu = self.table_rightclick.menu
        layout_table = [
            [sg.Table(
                self.get_table_from_database(),
                **attr.base_table,
                key=self.key_table,
                headings=self.columns,
                col_widths=[20 for _ in range(len(self.columns))],
                enable_click_events=True,
                right_click_menu=['&Right', menu] if menu else None,
                expand_y=True,
            )],
        ]

        layout = [
            layout_insert,
            layout_filter,
            layout_table_all,
            layout_table_selected,
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
        # Table
        self.table = self.window[self.key_table]
        self.table_click = TableClick(self.key_table, self.table)
        self.table_doubleclick = TableDoubleClick(self.key_table, self.table)
        # Call set method
        self.filter_layout.set(self._window)
        self.table_all_layout.set(self.table)
        self.table_rightclick.set(self.table, window=self._window, key_inputs=self.key_inputs)  # window and key_inputs are for copypaste
        self.table_selected_layout.set(self.table, window=self._window, key_inputs=self.key_inputs)  # window and key_inputs are for copypaste
        # Subwindows
        subwin_names = [self.key_description] + self.key_candidates + [self.key_update]
        self.subwin = SubWindow(self.window, subwin_names)

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
            SP.fatal_error(f'rows_gui({len(rows_gui)}) and rows_db({len(rows_db)}) have different line lengths')
        rows_large, rows_small, name_large, name_small = \
            (rows_db, rows_gui, 'DB', 'GUI') if len(rows_gui) < len(rows_db) else \
            (rows_gui, rows_db, 'GUI', 'DB')
        has_err = False
        for rl in rows_large[:]:
            rows_large.pop(0)
            try:
                rows_small.pop(rows_small.index(rl))
            except ValueError:
                SP.fatal_error(f'Only {name_large} has {rl}')
                has_err = True
        for rs in rows_small:
            SP.fatal_error(f'Only {name_small} has {rs}')
            has_err = True
        return has_err

    def close(self):
        if __debug__:
            if self._compare_tables():
                return
            SP.debug(f'TableWindow "{self.tname}" finished without any problems')
        super().close()

    def get_table_from_database(self):
        query = f'SELECT * FROM {self.tname};'
        ret = self.dbop.execute(query, ignore_error=True)
        if ret.is_error:
            SP.error([f'Wrong query: {query}', ret.show()], do_exit=False)
            return self.close()
        rows = self.dbop.fetchall()
        return rows

    # handle --->

    def handle(self, event, values):
        if isinstance(event, tuple):
            self.table_click.handle(event, values)
        elif event in self.key_description:
            self.open_table_infomation_window(event)
        elif event in self.key_candidates:
            self.open_candidate_window(event)
        elif event == self.key_insert:
            self.insert(values)
        elif event == self.key_clear:
            self.clear()
        elif event.startswith(self.filter_layout.prefkey):
            self.filter_layout.handle(event, values)
        elif event.startswith(self.table_all_layout.prefkey):
            self.table_all_layout.handle(event, values)
        elif event.startswith(self.table_selected_layout.prefkey):
            self.table_selected_layout.handle(event, values)
        elif event == self.key_update:
            self.update(values)
        elif event == self.key_delete:
            self.delete(values)
        elif event == self.table_doubleclick.key:
            self.table_doubleclick.handle(event, values)
        elif event == self.table_rightclick.key or event in self.table_rightclick.menu:
            self.table_rightclick.handle(event, values)

    # <--- handle

    def open_table_infomation_window(self, key):
        columns, data = self._desc_col_data
        location = get_location(self.window, keyy=key, dy=150)
        self.subwin.create_unique(key, TableDescriptionWindow, self.pack, self.tname, columns, data, location)

    def open_candidate_window(self, key):
        idx = int(key.split('.')[-1])
        #-----------------------------------------------
        #data = [d[idx] for d in self.table_data]
        # QUESTION: Slow performance?
        query = f'SELECT DISTINCT({self.columns[idx]}) FROM {self.tname}'
        ret = self.dbop.execute(query)
        if ret.is_error:
            SP.fatal_error(f'Bad query: {query}')
        data = [d[0] for d in self.dbop.fetchall()]
        #-----------------------------------------------
        element = self.window[self.key_inputs[idx]]
        location = get_location(self.window, key=self.key_inputs[idx], dy=35)
        self.subwin.create_unique(key, CandidateWindow, data, self.pack, element, location)

    def get_fields(self, primary_value):
        # FIXME: Codes should be rewritten to type conversions rather than query database
        column_str = ", ".join(self.columns)
        column_name = self.columns[self.pkidx]
        query = f'SELECT {column_str} from {self.tname} WHERE {column_name} = "{primary_value}"'
        ret = self.dbop.execute(query)
        if ret.is_error:
            SP.fatal_error(f'Bad querry: {query}')
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
        SP.info(f'Insert: {data}')

    def clear(self):
        for k in self.key_inputs:
            self.window[k].update('')

    def update(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            popup_error('Not selected', get_location(self.window, self.key_update))
        table_data = self.table.get()
        data = [table_data[r] for r in rows]
        location = get_location(self.window, keyy=self.key_update, dy=70)
        self.subwin.create_unique(self.key_update, TableUpdateWindow, self, self.pack, rows, self.tname, self.columns, data, table_data, location)

    def delete(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            popup_error('Not selected', get_location(self.window, self.key_delete))
        # Confirm deletion
        if self.cfg.confirm_deletion:
            loc = get_location(self.window, key=self.key_delete)
            ret = sg.popup_ok_cancel('Delete selected rows?', keep_on_top=True, location=loc)
            if ret == 'Cancel':
                return
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
        [SP.info(f'Delete: {list(d)}') for d in data]

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
        [SP.info(f'Update: {update}') for update in updates]

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
        self.key_cancel = f'{prefkey}cancel'
        self.key_inputs = [[f'{prefkey}{r}.{c}.input' for c in columns] for r in rows]

        layout = [
            [sg.Button('Update', **attr.base_button, button_color=attr.color_warning, key=self.key_update),
             sg.Button('Cancel', **attr.base_button, button_color=attr.color_safety, key=self.key_cancel)],
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
        elif event == self.key_cancel:
            self.cancel()

    def update(self):
        # Check
        try:
            if not all([self.selected_data[i] == self.table_data[r] for i, r in enumerate(self.rows)]):
                raise EASYDBO_USER_ERROR
        except (EASYDBO_USER_ERROR, IndexError):
            SP.error('Cannot update because table has been changed')
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

    def cancel(self):
        self.close()
