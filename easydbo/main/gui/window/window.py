import sys
import PySimpleGUI as sg
from .main import MainWindow
from easydbo.exception import EASYDBO_GOTO_LOOP


class Pack:
    def __init__(self, winmgr, configs, aliases, tableop, dbop):
        self.winmgr = winmgr
        self.configs = configs
        self.aliases = aliases
        self.tableop = tableop
        self.dbop = dbop


class WindowManger():
    def __init__(self, configs, aliases, tableop, dbop):
        pack = Pack(self, configs, aliases, tableop, dbop)
        select = MainWindow(pack)
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
