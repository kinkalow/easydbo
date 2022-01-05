import sys
from datetime import datetime

class BaseWindow:
    def __init__(self, winmgr):
        self.winmgr = winmgr

    def close(self):
        self.winmgr.remove_window(self.window)
        self.window.close()
        self._window = None

    def flush(self):
        sys.stdout.flush()

    def handle(self, event, values):
        pass

    def make_prefix_key(self, prefix, timestamp=False):
        return f'_{prefix}{int(datetime.now().timestamp())}__.' if timestamp else f'_{prefix}__.'

    def print(self, msg):
        print(msg)
        sys.stdout.flush()

    @property
    def window(self):
        return self._window


class SubWindowManager:
    def __init__(self, winmgr, main_window, names):
        self.winmgr = winmgr
        self.main_window = main_window
        self.sub_windows = {n: None for n in names}

    def get_location(self, widgetkey='', widgetx=False, widgety=False, dx=0, dy=0):
        if not widgetx or not widgety:
            x, y = self.main_window.CurrentLocation()
        if widgetx:
            x = self.main_window[widgetkey].Widget.winfo_rootx()
        if widgety:
            y = self.main_window[widgetkey].Widget.winfo_rooty()
        return (x + dx, y + dy)

    def create_window(self, window_class, *args, **kwargs):
        winobj = window_class(*args, **kwargs)
        self.winmgr.add_window(winobj)
        return winobj

    def create_single_window(self, name, window_class, *args, **kwargs):
        if self.sub_windows[name] in self.winmgr.windows:
            return
        winobj = self.create_window(window_class, *args, **kwargs)
        self.sub_windows[name] = winobj.window
