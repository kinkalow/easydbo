import sys
import PySimpleGUI as sg
from .main import MainWindow
from datetime import datetime
from easydbo.exception import EASYDBO_GOTO_LOOP


class Util:
    def __init__(self, winmgr, configs, aliases, tableop, dbop):
        self.winmgr = winmgr
        self.configs = configs
        self.aliases = aliases
        self.tableop = tableop
        self.dbop = dbop

        self.tnames = [t.name for t in tableop.get_tables()]
        self.columns = tableop.get_columns()
        self.fullcolumns = tableop.get_columns(full=True)

    def call(self, func_args):
        if func_args:
            func, args = func_args[0], func_args[1:]
            func(*args)

    def to_csv(self, header, data2d, delimiter=','):
        header_csv = delimiter.join(header)
        data_csv = '\n'.join([delimiter.join(d1) for d1 in data2d])
        data_csv = f'{data_csv}\n' if data_csv else data_csv
        return f'{header_csv}\n{data_csv}' if header else data_csv

    def make_timestamp_prefix(self, prefix):
        return f'_{prefix}{int(datetime.now().timestamp())}__.'


class WindowManger():

    def __init__(self, configs, aliases, tableop, dbop):
        util = Util(self, configs, aliases, tableop, dbop)
        select = MainWindow(util)
        self.windows = {select.window: select}
        self.main_window = select.window

    def add_window(self, winobj):
        self.windows.update({winobj.window: winobj})

    def remove_window(self, window):
        self.windows.pop(window)

    def close(self):
        [w.close() for w in list(self.windows.values()) if w.window]

    def run(self):
        while True:
            try:
                sys.stdout.flush()
                window, event, values = sg.read_all_windows()
                #print(window, event, values, window in self.windows)
                if event == sg.WIN_CLOSED:
                    if window == self.main_window:
                        self.close()
                        break
                    else:
                        self.windows[window].close()
                elif window in self.windows:
                    self.windows[window].handle(event, values)
            except EASYDBO_GOTO_LOOP as e:
                print(e)
