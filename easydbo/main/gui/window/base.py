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

    def print(self, msg):
        print(msg)
        sys.stdout.flush()

    def flush(self):
        sys.stdout.flush()
