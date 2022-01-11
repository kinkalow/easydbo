import sys
import PySimpleGUI as sg
from easydbo.exception import EASYDBO_GOTO_LOOP
from .main import MainWindow
from .manager import WindowManager


class Pack:
    def __init__(self, configs, aliases, tableop, dbop):
        self.configs = configs
        self.aliases = aliases
        self.tableop = tableop
        self.dbop = dbop


class Application():
    def __init__(self, configs, aliases, tableop, dbop):
        pack = Pack(configs, aliases, tableop, dbop)
        select = MainWindow(pack)
        self.winmgr = WindowManager()
        self.winmgr.add(select)
        self.main_window = select.window

    def loop(self):
        while True:
            try:
                sys.stdout.flush()
                window, event, values = sg.read_all_windows()
                #print(window, event, values, window in self.windows)
                if event == sg.WIN_CLOSED:
                    if window == self.main_window:
                        self.winmgr.close()
                        break
                    else:
                        self.winmgr.windows[window].close()
                elif window in self.winmgr.windows:
                    self.winmgr.windows[window].handle(event, values)
            except EASYDBO_GOTO_LOOP as e:
                print(e)
