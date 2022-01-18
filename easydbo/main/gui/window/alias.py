import PySimpleGUI as sg
from .base import BaseWindow
from .common.layout.attribution import Attribution as attr
from .common.sql import create_query_result_window
from ..manager import SubWindow
from .common.log import Log


class AliasWindow(BaseWindow):
    def __init__(self, pack, location, parent_alias_method, size=None):
        self.pack = pack
        self.parent_alias_method = parent_alias_method

        self.aliasmgr = pack.aliasmgr
        aliases = self.aliasmgr.reload()
        self.phconv = self.aliasmgr.phconv

        self.prefkey = prefkey = self.make_prefix_key('alias')
        self.key_reload = f'{prefkey}reload'
        self.key_buttons = [f'{prefkey}{a.name}.button' for a in aliases]
        self.key_scroll = f'{prefkey}scroll'
        self.key_querys = [f'{prefkey}{a.name}.placeholder' for a in aliases]
        self.key_placeholders = {}  # Dict{index: List} ... Define below

        self.querys = [a.query for a in aliases]

        maxlen = max(len(a.name) for a in aliases)
        layout = []
        for i, a in enumerate(aliases):
            n_mark = self.phconv.count(a.query)
            layout.append([
                sg.Button(a.name, **attr.base_button_with_color_safety, key=self.key_buttons[i], size=(maxlen, 1)),
                sg.InputText(a.query, **attr.base_inputtext, key=self.key_querys[i], size=(200, 1), expand_x=True),  # Do not extend in x direction, so add size
            ])
            # placeholders
            if n_mark > 0:
                keys = [f'{prefkey}{a.name}.mark.{j}' for j in range(n_mark)]
                self.key_placeholders[i] = keys
                layout.append(
                    [sg.Button('', **attr.base_button_with_color_safety, key=self.key_buttons[i], size=(maxlen, 1))]
                    + [sg.InputText('', **attr.base_inputtext, key=keys[j], size=(19, 1)) for j in range(n_mark)]
                )
        layout = [
            [sg.Button('Reload', **attr.base_button_with_color_safety, key=self.key_reload)],
            [sg.Column(layout, key=self.key_scroll, pad=(0, 0), expand_x=True, expand_y=True,
                       scrollable=True, vertical_scroll_only=True)],
        ]

        self._window = sg.Window(
            'EasyDBO Alias',
            layout,
            finalize=True,
            location=location,
            resizable=True,
            size=size if size else (1300, 800),
        )
        subwin_names = self.key_buttons
        self.subwin = SubWindow(self.window, subwin_names)

        frame_id = self.window[self.key_scroll].Widget.frame_id
        canvas = self.window[self.key_scroll].Widget.canvas
        canvas.bind('<Configure>', lambda event, canvas=canvas, frame_id=frame_id:
                    canvas.itemconfig(frame_id, width=canvas.winfo_width()))

    def handle(self, event, values):
        if event == self.key_reload:
            self.reload()
        elif event in self.key_buttons:
            key = '.'.join(event.split('.')[:-1] + [self.key_querys[0].split('.')[-1]])
            self.query(event, values[key])

    def reset(self):
        [self.window[k].Update(v) for k, v in zip(self.key_querys, self.querys)]

    def reload(self):
        if self.aliasmgr.is_modified():
            location = self.subwin.get_location()
            size = self.window.Size
            self.close()
            self.parent_alias_method(location=location, size=size)
        else:
            self.reset()

    def query(self, key, query):
        # Process placeholders
        idx = self.key_buttons.index(key)
        if idx in self.key_placeholders:
            key_phs = self.key_placeholders[idx]
            phvals = [self.window[k].get() for k in key_phs]
            for v in phvals:
                if not v:
                    return Log.miss(f'Missing placeholder values for alias({key.split(".")[1]})')
            query = self.phconv.convert(query, phvals)
        # Create window
        location = self.subwin.get_location(widgetkey=key, widgetx=True, widgety=True, dy=60)
        create_query_result_window(query, self.pack, self.subwin, location)
