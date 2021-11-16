class BaseLayout:
    def bind(self, window):
        pass

    def handle(self, event, values):
        pass

    def get_layout(self):
        return self.layout

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

    def filter_values_by_prefix_key(self, prefkey, values):
        return {k: v for k, v in values.items()
                if isinstance(k, str) and k.startswith(prefkey)}
