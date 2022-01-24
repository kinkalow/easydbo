import PySimpleGUI as sg
from easydbo.output.print_ import SimplePrint as SP
from .base import BaseWindow
from .common.layout.attribution import Attribution as attr
from .common.layout.filter import FilterLayout
from .common.layout.table import TableAllLayout, TableSelectedLayout, TableRightClick, TableClick, TableDoubleClick
from .common.popup import popup_error
from .common.util import get_location
from ..manager import SubWindow

class QueryResultWindow(BaseWindow):
    def __init__(self, pack, query, columns, table_data, location):
        self.pack = pack
        self.query = query
        self.table_data = table_data
        self.cfg = cfg = pack.configs.table_window

        length = len(columns[0])

        self.prefkey = prefkey = self.make_prefix_key('result', timestamp=True)
        self.key_querybtn = f'{prefkey}querybutton'
        self.key_querytxt = f'{prefkey}querytext'
        self.key_table = f'{prefkey}table'

        # layout_query_button
        layout_query_button = [
            sg.Button('Query', **attr.base_button_with_color_safety, key=self.key_querybtn),
            sg.Text(query, **attr.base_text, key=self.key_querytxt),
        ]

        # layout_filter
        self.filter_layout = FilterLayout(prefkey, columns, self.key_table, pack.dbop, self.query, display_columns=True)
        layout_filter = self.filter_layout.layout

        # layout_table_all
        self.table_all_layout = TableAllLayout(
            prefkey, enable_save=cfg.enable_all_save,
            enable_print=cfg.enable_all_print, enable_greprun=cfg.enable_all_greprun)
        layout_table_all = self.table_all_layout.layout

        # layout_table_selected
        self.table_selected_layout = TableSelectedLayout(
            prefkey, self.key_table, enable_copypaste=False,
            enable_save=cfg.enable_selected_save, enable_print=cfg.enable_selected_print, enable_frame=True)
        layout_table_selected = self.table_selected_layout.layout

        # layout_table
        self.table_rightclick = TableRightClick(
            self.key_table,
            enable_cell_copypaste=False, enable_cell_print=cfg.enable_rightclick_cell_print,
            enable_row_copypaste=False, enable_row_print=cfg.enable_rightclick_row_print,
            enable_selected_copypaste=False, enable_selected_print=cfg.enable_rightclick_selected_print, enable_selected_save=cfg.enable_rightclick_selected_save,
            enable_all_print=cfg.enable_rightclick_all_print, enable_all_save=cfg.enable_rightclick_all_save)
        menu = self.table_rightclick.menu
        layout_table = [
            [sg.Table(
                table_data,
                **attr.base_table,
                key=self.key_table,
                headings=columns,
                col_widths=[20 for _ in range(length)],
                enable_click_events=True,
                right_click_menu=['&Right', menu] if menu else None,
                expand_y=True,
            )]
        ]

        self.layout = [
            layout_query_button,
            layout_filter,
            layout_table_all,
            layout_table_selected,
            layout_table,
        ]

        self._window = sg.Window(
            'EasyDBO QueryResult',
            self.layout,
            finalize=True,
            location=location,
            resizable=True,
            size=(1300, 800),
        )
        # Table
        self.table = self.window[self.key_table]
        self.table_click = TableClick(self.key_table, self.table)
        self.table_doubleclick = TableDoubleClick(self.key_table, self.table)
        # Call set method
        self.filter_layout.set(self._window)
        self.table_all_layout.set(self.table)
        self.table_rightclick.set(self.table)
        self.table_selected_layout.set(self.table)
        # Subwindows
        self.subwin = SubWindow(self.window, [self.key_querybtn])

        #frame_id = self.window[self.key_table].Widget.frame_id
        #canvas = self.window[self.key_table].Widget.canvas
        #canvas.bind('<Configure>', lambda event, canvas=canvas, frame_id=frame_id:
        #            canvas.itemconfig(frame_id, width=canvas.winfo_width()))

    def get_table_data(self):
        columns = self.window[self.key_table].ColumnHeadings
        data = self.window[self.key_table].get()
        return columns, data

    def handle(self, event, values):
        if isinstance(event, tuple):
            self.table_click.handle(event, values)
        elif event == self.key_querybtn:
            self.add_alias(event)
        elif event.startswith(self.filter_layout.prefkey):
            self.filter_layout.handle(event, values)
        elif event.startswith(self.table_all_layout.prefkey):
            self.table_all_layout.handle(event, values)
        elif event.startswith(self.table_selected_layout.prefkey):
            self.table_selected_layout.handle(event, values)
        elif event == self.table_doubleclick.key:
            self.table_doubleclick.handle(event, values)
        elif event == self.table_rightclick.key or event in self.table_rightclick.menu:
            self.table_rightclick.handle(event, values)

    def add_alias(self, key):
        location = get_location(self.window, keyy=key, dy=70)
        self.subwin.create_unique(key, QuerySaveWindow, self.pack, self.query, location)


class QuerySaveWindow(BaseWindow):
    def __init__(self, pack, query, location):
        self.aliasmgr = pack.aliasmgr

        prefkey = self.make_prefix_key('saveasalias', timestamp=True)
        self.key_save = f'{prefkey}save'
        self.key_cancel = f'{prefkey}cancel'
        self.key_alias = f'{prefkey}alias'
        self.key_query = f'{prefkey}query'

        self.layout = [
            [
                sg.Button('Save', **attr.base_button_with_color_safety, key=self.key_save),
                sg.Button('Close', **attr.base_button_with_color_safety, key=self.key_cancel),
            ],
            [
                sg.Text('Alias', **attr.base_text, size=(5, 1)),
                sg.InputText('', **attr.base_inputtext, key=self.key_alias),
            ],
            [
                sg.Text('Query', **attr.base_text, size=(5, 1)),
                sg.Multiline(query, **attr.base_multiline, key=self.key_query, expand_x=True, expand_y=True, size=(1300, 500)),
            ],
        ]

        self._window = sg.Window(
            'EasyDBO QuerySave',
            self.layout,
            finalize=True,
            location=location,
            resizable=True,
            size=(1300, 500),
        )

    def handle(self, event, values):
        if event == self.key_save:
            self.save(event)
        elif event == self.key_cancel:
            self.cancel()

    def save(self, key):
        name = self.window[self.key_alias].get()
        if name == '':
            popup_error('Missing alias name', get_location(self.window, key=key))
        # Check
        idx_update = self.aliasmgr.index(name)
        if idx_update != -1:
            loc = get_location(self.window, key=key)
            ret = sg.popup_ok_cancel('Overwrite alias?', keep_on_top=True, location=loc)
            if ret == 'Cancel':
                return
        # Add or Update
        query = self.window[self.key_query].get()
        if idx_update == -1:
            self.aliasmgr.insert(0, name, query)
            add_or_update = 'Add'
        else:
            self.aliasmgr.update(name, query, index=idx_update)
            add_or_update = 'Update'
        # Update file
        self.aliasmgr.save()
        SP.info(f'{add_or_update} alias: {name}')
        self.close()

    def cancel(self):
        self.close()
