import sys
import PySimpleGUI as sg
from .select import SelectWindow
from datetime import datetime


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

    def get_column(self, tname):
        return self.tableop.get_columns([tname])[0]

    def call(self, func_args):
        if func_args:
            func, args = func_args[0], func_args[1:]
            func(*args)

    def make_timestamp_prefix(self, prefix):
        return f'_{prefix}{int(datetime.now().timestamp())}__.'

class WindowManger():

    def __init__(self, configs, aliases, tableop, dbop):
        util = Util(self, configs, aliases, tableop, dbop)
        select = SelectWindow(self, util)
        self.windows = {select.get_window(): select}
        self.main_window = select

    def add_window(self, winobj):
        self.windows.update({winobj.get_window(): winobj})

    def close(self):
        for i, sub in enumerate(self.windows):
            if sub.window:
                sub.close()
        super().close()

    def run(self):
        while True:
            sys.stdout.flush()
            window, event, values = sg.read_all_windows()
            #print(window, event, values, window in self.windows)
            if event == sg.WIN_CLOSED:
                if window == self.main_window:
                    for w in self.windows.values():
                        w.close()
                    break
                else:
                    self.windows[window].close()
            elif window in self.windows:
                self.windows[window].handle(event, values)
