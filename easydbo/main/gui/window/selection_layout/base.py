import sys

class BaseLayout:
    def filter_values_by_prefix_key(self, prefkey, values):
        return {k: v for k, v in values.items()
                if isinstance(k, str) and k.startswith(prefkey)}

    def handle(self, event, values):
        pass

    def get_privatekey(self):
        return self.prefkey

    def get_layout(self):
        return self.layout

    def print(self, msg):
        print(msg)
        sys.stdout.flush()

    def remove_prefix_key(self, prefkey, event='', values={}):
        len_ = len(prefkey)
        event = event[len_:] if event else event
        values = {k[len_:]: v for k, v in values.items()
                  if isinstance(k, str) and k.startswith(prefkey)} if values else values
        if event and values:
            return event, values
        elif event:
            return event
        elif values:
            return values
        else:
            return

    def set_window(self, window):
        self.window = window
