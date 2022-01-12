from datetime import datetime
from ..manager import WindowManager


class BaseWindow:
    '''
    Classes that inherit from BaseWindow must set sg.Window instance to self._window
    handle(...) is abstract method
    '''

    def close(self):
        WindowManager().remove(self.window)
        self.window.close()
        self._window = None

    def handle(self, event, values):
        pass

    def make_prefix_key(self, prefix, timestamp=False):
        return f'_{prefix}{int(datetime.now().timestamp())}__.' if timestamp else f'_{prefix}__.'

    @property
    def window(self):
        return self._window
