import re
import PySimpleGUI as sg
from easydbo.main.gui.window.common.command import make_grep_command, save_table_data
from easydbo.main.gui.window.common.command import execute_table_command
from easydbo.output.print_ import SimplePrint as SP

def copypaste_cell(table, window, keys, row, col):
    data = table.get()[row][col]
    window[keys[col]].update(data)

def copypaste_row(table, window, keys, row):
    data = table.get()[row]
    for k, d in zip(keys, data):
        window[k].update(d)

def greprun(table, pattern, columns=[], data=[[]], delimiter=',', show_command=True):
    '''
    table    : sg.Table       :
    pattern  : str            : Specify a pattern for the grep command
    columns  : List(str)      : Specified names are output
    data     : List[List(any)]: Target data
    delimiter: str            :
    '''
    pattern = make_grep_command(pattern)
    if not pattern or re.search(r'>', pattern):  # Prevent redirection
        return
    columns, data = _get_columns_data(table, columns, data)
    cmd = f'column -t -s {delimiter} {{path}} | {pattern}'
    execute_table_command(cmd, columns, data, delimiter, show_command)

def print_cell(table, row, col):
    data = table.get()[row][col]
    SP.output(data)

def print_rows(table, rows=[], is_all=False):
    '''
    table : sg.Table:
    rows  : List    : Specify row numbers in table to be saved
    is_all: bool    : If True, save all rows in table
    '''
    if not rows and not is_all:
        return
    data = table.get()
    if not is_all:
        data = [data[r] for r in rows]
    _prettyrun(table, data=data)

def save_as_csv(table, rows=[], is_all=False):
    '''
    table : sg.Table:
    rows  : List    : Specify row numbers in table to be saved
    is_all: bool    : If True, save all rows in table
    '''
    if not rows and not is_all:
        return
    path = sg.popup_get_file('Save', save_as=True, no_window=True, file_types=(('CSV', '.csv'),))
    if not path:
        return
    data = table.get()
    if not is_all:
        data = [data[r] for r in rows]
    save_table_data(path, table.ColumnHeadings, data)

def sort(table, idx_column, is_reverse):
    table_data = table.get()
    table_data.sort(key=lambda k: k[idx_column], reverse=is_reverse)
    table.update(table_data)


def _get_columns_data(table, columns, data):
    columns = columns if columns else table.ColumnHeadings
    data = data if data != [[]] else table.get()
    return columns, data

def _prettyrun(table, columns=[], data=[[]], delimiter=',', show_command=False):
    columns, data = _get_columns_data(table, columns, data)
    cmd = f'column -t -s {delimiter} {{path}}'
    execute_table_command(cmd, columns, data, delimiter, show_command)
