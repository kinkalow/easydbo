import sys

class BaseWindow:
    def __init__(self):
        self.window = None

    def handle(self, event, values):
        pass

    def close(self):
        self.window.close()
        self.window = None

    def get_window(self):
        return self.window

    def get_widget_location(self, key):
        x = self.window[key].Widget.winfo_rootx()
        y = self.window[key].Widget.winfo_rooty()
        return (x, y)

    def print(self, msg):
        print(msg)
        sys.stdout.flush()

    def flush(self):
        sys.stdout.flush()
