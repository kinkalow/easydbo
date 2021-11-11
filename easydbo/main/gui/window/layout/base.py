class BaseLayout:
    def bind(self, window):
        pass

    def handle(self, event, values):
        pass

    def get_layout(self):
        return self.layout

    def remove_prefix_key(self, prefkey, event, values):
        len_ = len(prefkey)
        event = event[len_:]
        values = {k[len_:]: v for k, v in values.items()
                  if isinstance(k, str) and k.startswith(prefkey)}
        return event, values
