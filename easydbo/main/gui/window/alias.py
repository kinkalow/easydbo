import PySimpleGUI as sg
from .common.layout import Attribution as attr
from .base import BaseWindow, SubWindowManager
from easydbo.init.alias import AliasLoader
from .common.sql import create_sql_result

class AliasWindow(BaseWindow):
    def __init__(self, util, location, parent_alias_method, size=None):
        super().__init__(util.winmgr)
        self.util = util
        self.parent_alias_method = parent_alias_method

        self.prefkey = prefkey = '_alias__.'
        #aliases = util.aliases
        aliases = AliasLoader().get()
        placeholder_mark = '?'
        self.key_reset = f'{prefkey}reset'
        self.key_reload = f'{prefkey}reload'
        self.key_aliasnames = [f'{prefkey}{a.name}.button' for a in aliases]
        self.key_scroll = f'{prefkey}scroll'
        self.key_inputs = [f'{prefkey}{a.name}.inputtext' for a in aliases]
        self.key_mark = []  # Define below

        self.sqls = [a.sql for a in aliases]

        maxlen = max(len(a.name) for a in aliases)
        layout = []
        for i, a in enumerate(aliases):
            n_qestionmark = len(a.sql.split(placeholder_mark)) - 1
            layout.append([
                sg.Button(a.name, **attr.base_button_with_color_safety, key=self.key_aliasnames[i], size=(maxlen, 1)),
                sg.InputText(a.sql, **attr.base_inputtext, key=self.key_inputs[i], size=(200, 1), expand_x=True),  # Do not extend in x direction only first if size is not present
            ])
            # placeholders
            if n_qestionmark > 0:
                keys = [f'{prefkey}{a.name}.mark.{j}' for j in range(n_qestionmark)]
                self.key_mark.append(keys)
                layout.append(
                    [sg.Button('', **attr.base_button_with_color_safety, key=self.key_aliasnames[i], size=(maxlen, 1))]
                    + [sg.InputText('', **attr.base_inputtext, key=keys[j], size=(19, 1)) for j in range(n_qestionmark)]
                )
        layout = [
            [sg.Button('Reset', **attr.base_button_with_color_safety, key=self.key_reset),
             sg.Button('Reload', **attr.base_button_with_color_safety, key=self.key_reload)],
            [sg.Column(layout, key=self.key_scroll, pad=(0, 0), expand_x=True, expand_y=True,
                       scrollable=True, vertical_scroll_only=True)],
        ]

        self._window = sg.Window(
            'EasyDBO Alias',
            layout,
            size=size if size else (1300, 800),
            resizable=True,
            finalize=True,
            location=location,
        )
        subwin_names = self.key_aliasnames
        self.subwinmgr = SubWindowManager(util.winmgr, self.window, subwin_names)

        frame_id = self.window[self.key_scroll].Widget.frame_id
        canvas = self.window[self.key_scroll].Widget.canvas
        canvas.bind('<Configure>', lambda event, canvas=canvas, frame_id=frame_id:
                    canvas.itemconfig(frame_id, width=canvas.winfo_width()))

    def handle(self, event, values):
        if event in self.key_reset:
            self.reset()
        elif event == self.key_reload:
            self.reload()
        elif event in self.key_aliasnames:
            key_value = '.'.join(event.split('.')[:-1] + [self.key_inputs[0].split('.')[-1]])
            self.query(event, values[key_value])

    def reset(self):
        [self.window[k].Update(v) for k, v in zip(self.key_inputs, self.sqls)]

    def reload(self):
        location = self.subwinmgr.get_location()
        size = self.window.Size
        self.close()
        self.parent_alias_method(location=location, size=size)

    def query(self, key, query):
        location = self.subwinmgr.get_location(widgetkey=key, widgetx=True, widgety=True, dy=60)
        create_sql_result(query, self.util, self.subwinmgr, location)
