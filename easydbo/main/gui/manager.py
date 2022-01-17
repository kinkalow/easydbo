class WindowManager():
    _windows = {}

    @classmethod
    def add(self, winobj):
        self._windows.update({winobj.window: winobj})

    @classmethod
    def remove(self, window):
        self._windows.pop(window)

    @classmethod
    def close(self):
        [w.close() for w in list(self._windows.values()) if w.window]
        assert(len(self._windows) == 0)

    @property
    def windows(self):
        return self._windows


class SubWindow:
    def __init__(self, main_window, names):
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

    def create_multiples(self, window_class, *args, **kwargs):
        winobj = window_class(*args, **kwargs)
        WindowManager().add(winobj)
        return winobj

    def create_unique(self, name, window_class, *args, **kwargs):
        if self.sub_windows[name] in WindowManager().windows:
            #self.sub_windows[name].bring_to_front()  # Does not work
            return
        winobj = self.create_multiples(window_class, *args, **kwargs)
        self.sub_windows[name] = winobj.window
