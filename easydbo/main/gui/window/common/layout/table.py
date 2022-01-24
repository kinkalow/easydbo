import PySimpleGUI as sg
from .base import BaseLayout
from easydbo.main.gui.window.common.layout.attribution import Attribution as attr
from easydbo.main.gui.window.common.action.table import copypaste_cell, copypaste_row, greprun, print_cell, print_rows, save_as_csv, sort
from easydbo.main.gui.window.common.popup import popup_error
from easydbo.main.gui.window.common.util import get_location


class TableAllLayout(BaseLayout):
    def __init__(self, caller_prefkey, enable_save=True, enable_print=True, enable_greprun=True, enable_frame=True):
        """
        caller_prefkey: str: Caller prefix key
        NOTE: Caller must call self.set()
        """
        prefkey = f'{caller_prefkey}tableall.'
        self.key_saveall = f'{prefkey}saveall'
        self.key_printall = f'{prefkey}printall'
        self.key_greprun = f'{prefkey}grepbtn'
        self.key_greptext = f'{prefkey}greptext'

        layout = []
        if enable_save:
            layout.append(sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_saveall))
        if enable_print:
            layout.append(sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printall))
        if enable_greprun:
            layout.append(sg.Button('GrepRun', **attr.base_button_with_color_safety, key=self.key_greprun))
            layout.append(sg.InputText('', **attr.base_inputtext, key=self.key_greptext))
        if enable_frame and layout:
            layout = [sg.Frame('All', [layout], title_location=sg.TITLE_LOCATION_RIGHT)]

        self._prefkey = prefkey
        self._layout = layout

    def set(self, table):
        self.table = table

    def handle(self, event, values):
        if event == self.key_saveall:
            save_as_csv(self.table, is_all=True)
        elif event == self.key_printall:
            print_rows(self.table, is_all=True)
        elif event == self.key_greprun:
            greprun(self.table, values[self.key_greptext])


class TableSelectedLayout(BaseLayout):
    def __init__(self, caller_prefkey, key_table, enable_copypaste=False, enable_save=True, enable_print=True, enable_frame=True):
        """
        caller_prefkey: str: Caller prefix key
        NOTE: Caller must call self.set()
        """
        self.key_table = key_table

        prefkey = f'{caller_prefkey}tableselected.'
        self.key_copypasterow = f'{prefkey}copypasterow'
        self.key_saveselected = f'{prefkey}saveselected'
        self.key_printselected = f'{prefkey}printselected'

        layout = []
        if enable_copypaste:
            layout.append(sg.Button('CopyPaste', **attr.base_button_with_color_safety, key=self.key_copypasterow))
        if enable_save:
            layout.append(sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_saveselected))
        if enable_print:
            layout.append(sg.Button('Print', **attr.base_button_with_color_safety, key=self.key_printselected))
        if enable_frame and layout:
            layout = [sg.Frame('Selected', [layout], title_location=sg.TITLE_LOCATION_RIGHT)],

        self._prefkey = prefkey
        self._layout = layout

    def set(self, table, window=None, key_inputs=None):
        self.table = table
        self.window = window
        self.key_inputs = key_inputs

    def handle(self, event, values):
        rows = values[self.key_table]
        if not rows and event in (self.key_copypasterow, self.key_saveselected, self.key_printselected):
            popup_error('Not selected', get_location(self.window, event))
        if event == self.key_copypasterow:
            copypaste_row(self.table, self.window, self.key_inputs, rows[0])
        if event == self.key_saveselected:
            save_as_csv(self.table, rows)
        elif event == self.key_printselected:
            print_rows(self.table, rows)


class TableRightClick():
    def __init__(self, key_table,
                 enable_cell_copypaste=False, enable_cell_print=True,
                 enable_row_copypaste=False, enable_row_print=True,
                 enable_selected_copypaste=False, enable_selected_print=True, enable_selected_save=True,
                 enable_all_print=True, enable_all_save=True):
        """
        NOTE: Caller calls menu() and key()
        """

        self.key_table = key_table
        self.rightclick_location = (-1, -1)

        key_rightclick = f'{key_table}.rightclick'
        #
        self.key_cell_copypaste = '[Cell] CopyPaste'
        self.key_cell_print = '[Cell] Print'
        self.key_row_copypaste = '[Row] CopyPaste'
        self.key_row_print = '[Row] Print'
        self.key_selected_copypaste = '[Selected] CopyPaste'
        self.key_selected_print = '[Selected] Print'
        self.key_selected_save = '[Selected] Save'
        self.key_all_print = '[All] Print'
        self.key_all_save = '[All] Save'

        separator_line = '-' * 30
        menu = []
        if enable_cell_copypaste:
            menu.append(self.key_cell_copypaste)
        if enable_cell_print:
            menu.append(self.key_cell_print)
        if enable_cell_copypaste or enable_cell_print:
            menu.append(separator_line)
        if enable_row_copypaste:
            menu.append(self.key_row_copypaste)
        if enable_row_print:
            menu.append(self.key_row_print)
        if enable_row_copypaste or enable_row_print:
            menu.append(separator_line)
        if enable_selected_copypaste:
            menu.append(self.key_selected_copypaste)
        if enable_selected_print:
            menu.append(self.key_selected_print)
        if enable_selected_save:
            menu.append(self.key_selected_save)
        if enable_selected_copypaste or enable_selected_print or enable_selected_save:
            menu.append(separator_line)
        if enable_all_print:
            menu.append(self.key_all_print)
        if enable_all_save:
            menu.append(self.key_all_save)

        self._key_rightclick = key_rightclick
        self._menu = menu

    @property
    def menu(self):
        return self._menu

    @property
    def key(self):
        return self._key_rightclick

    def set(self, table, window=None, key_inputs=None):
        self.table = table
        self.window = window
        self.key_inputs = key_inputs
        #
        table.bind('<Button-3>', f'.{self._key_rightclick.split(".")[-1]}')

    def handle(self, event, values):
        if event == self._key_rightclick:
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
        elif event in self._menu:
            if self.rightclick_location == (-1, -1):
                return
            row, col = self.rightclick_location[0] - 1, self.rightclick_location[1] - 1
            if row == -1:  # Ignore header line
                return
            # Cell
            if event == self.key_cell_copypaste:
                copypaste_cell(self.table, self.window, self.key_inputs, row, col)
            elif event == self.key_cell_print:
                print_cell(self.table, row, col)
            # Row
            elif event == self.key_row_copypaste:
                copypaste_row(self.table, self.window, self.key_inputs, row)
            elif event == self.key_row_print:
                print_rows(self.table, rows=[row])
            # Selected
            elif event == self.key_selected_copypaste:
                rows = values[self.key_table]
                if rows:
                    copypaste_row(self.table, self.window, self.key_inputs, rows[0])
            elif event == self.key_selected_print:
                print_rows(self.table, rows=values[self.key_table])
            elif event == self.key_selected_save:
                save_as_csv(self.table, rows=values[self.key_table])
            # All
            elif event == self.key_all_print:
                print_rows(self.table, is_all=True)
            elif event == self.key_all_save:
                save_as_csv(self.table, is_all=True)


class TableClick():
    def __init__(self, key_table, table):
        '''
        NOTE: table must have "enable_click_events=True"
        '''
        self.key_table = key_table
        self.table = table
        self.sort_reverse = True

    def handle(self, event, values):
        if event[0:2] == (self.key_table, '+CICKED+'):
            row, col = event[2]
            if row == -1:  # True when header line clicked
                try:
                    sort(self.table, col, self.sort_reverse)
                    self.sort_reverse = not self.sort_reverse
                except TypeError:
                    # If None is included, it may raise an exception
                    pass


class TableDoubleClick():
    def __init__(self, key_table, table):
        """
        NOTE: Caller calls key()
        """
        self.key_table = key_table
        self.key_doubleclick = f'{key_table}.doubleclick'
        self.table = table
        table.bind('<Double-Button-1>', f'.{self.key_doubleclick.split(".")[-1]}')

    @property
    def key(self):
        return self.key_doubleclick

    def handle(self, event, values):
        if event == self.key_doubleclick:
            print_rows(self.table, rows=values[self.key_table])
