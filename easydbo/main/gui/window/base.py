import sys

class BaseWindow:
    def __init__(self, winmgr):
        self.window = None
        self.winmgr = winmgr

    def handle(self, event, values):
        pass

    def close(self):
        self.winmgr.remove_window(self.window)
        self.window.close()
        self.window = None

    def get_window(self):
        return self.window

    def get_location(self, widgetkey='', widgetx=False, widgety=False, dx=0, dy=0):
        if not widgetx or not widgety:
            x, y = self.window.CurrentLocation()
        if widgetx:
            x = self.window[widgetkey].Widget.winfo_rootx()
        if widgety:
            y = self.window[widgetkey].Widget.winfo_rooty()
        return (x + dx, y + dy)

    def print(self, msg):
        print(msg)
        sys.stdout.flush()

    def flush(self):
        sys.stdout.flush()
