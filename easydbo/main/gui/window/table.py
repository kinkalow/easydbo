import PySimpleGUI as sg
from .base import BaseWindow
from .layout.common import Attribution as attr

class TableWindow(BaseWindow):
    def __init__(self, util, tname, on_close=None, parent_loc=()):
        self.tname = tname
        self.util = util
        self.columns = util.get_column(tname)
        self.dbop = util.dbop

        self.on_close = on_close

        self.prefkey = prefkey = f'_table{tname}__.'
        self.key_tname = f'{prefkey}{tname}'
        self.key_columns = [f'{prefkey}{c}' for c in self.columns]
        self.key_inputs = [f'{prefkey}{c}.input' for c in self.columns]
        self.key_insert = f'{prefkey}insert'
        self.key_clear = f'{prefkey}reset'
        self.key_copypaste = f'{prefkey}copypaste'
        self.key_update = f'{prefkey}update'
        self.key_print = f'{prefkey}print'
        self.key_save = f'{prefkey}save'
        self.key_delete = f'{prefkey}delete'
        self.key_table = f'{prefkey}table'
        self.key_table_click = f'{prefkey}table.click'
        self.key_table_doubleclick = f'{prefkey}table.doubleclick'

        commands = ['Copy', 'Delete', 'Update']

        layout = [
            [sg.Text(f' {self.tname} ', **attr.text_table, key=self.key_tname)],
            [sg.Text(c, **attr.base_text, key=self.key_columns[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [sg.InputText('', **attr.base_inputtext, key=self.key_inputs[i], size=(20, 1)) for i, c in enumerate(self.columns)],
            [
                sg.Button('Insert', **attr.base_button, button_color=attr.color_warning, key=self.key_insert),
                sg.Button('Clear', **attr.base_button, button_color=attr.color_safe, key=self.key_clear),
            ],
            [sg.Text()],
            [
                sg.Button('CopyPaste', **attr.base_button, key=self.key_copypaste, button_color=attr.color_safe),
                sg.Button('Print', **attr.base_button, key=self.key_print, button_color=attr.color_safe),
                sg.Button('Save', **attr.base_button, key=self.key_save, button_color=attr.color_safe),
                sg.Button('Update', **attr.base_button, key=self.key_update, button_color=attr.color_warning),
                sg.Button('Delete', **attr.base_button, key=self.key_delete, button_color=attr.color_danger),
            ],
            [sg.Table(
                [['' for _ in range(len(self.columns))]],
                key=self.key_table,
                headings=self.columns,
                auto_size_columns=False,
                enable_events=True,
                right_click_menu=['&Right', commands],
                col_widths=[20 for _ in range(len(self.columns))],
            )],
        ]

        self.window = sg.Window(
            f'EasyDBO {self.tname}',
            layout,
            size=(1200, 500),
            resizable=True,
            finalize=True,
            location=(30, 30),
        )
        if parent_loc:
            self.window.move(parent_loc[0], parent_loc[1] + 30)
        self.table = self.window[self.key_table]
        self.table.bind('<Double-Button-1>', f'.{self.key_table_doubleclick.split(".")[-1]}')

        self.table_data = self._show_table_data()

    def _show_table_data(self):
        cmd = f'SELECT * FROM {self.tname};'
        data = self.dbop.execute(cmd, ret=True)
        self.window[self.key_table].update(data)
        return data

    def close(self):
        self.window.close()
        self.window = None
        self.util.call(self.on_close)

    def handle(self, event, values):
        if event == self.key_insert:
            self.insert(values)
        elif event == self.key_clear:
            self.clear()
        elif event == self.key_copypaste:
            self.copypaste(values)
        elif event == self.key_update:
            self.update(values)
        elif event == self.key_delete:
            self.delete(values)
        elif event == self.key_table_doubleclick:
            pass
            #self.doubleclick(values)

    def insert(self, values):
        data = [self.window[k].get() for k in self.key_inputs]
        # Update
        self.dbop.insert(self.tname, self.columns, [data])
        self.dbop.commit()
        self.table_data.insert(0, data)
        self.window[self.key_table].update(self.table_data)
        #
        print(f'Insert: {data}')

    def clear(self):
        for k in self.key_inputs:
            self.window[k].update('')

    def copypaste(self, values):
        rows = values[self.key_table]
        if not rows:
            return
        data = self.table_data[rows[0]]
        for k, d in zip(self.key_inputs, data):
            self.window[k].update(d)

    def get_table_data(self, rows):
        return [self.table_data[r] for r in rows]

    def update(self, values):
        rows = sorted(values[self.key_table])
        if not rows:
            return
        data = self.get_table_data(rows)
        location = self.window.CurrentLocation()
        winobj = TableChangeWindow(self, self.util, rows, self.tname, self.columns, data, self.table_data, parent_loc=location)
        self.util.winmgr.add_window(winobj)

    def notify_update(self, rows, updates):
        for r, u in zip(rows, updates):
            self.table_data[r] = u
        self.window[self.key_table].update(self.table_data)
        [print(f'Update: {update}') for update in updates]

    def delete(self, values):
        table = self.util.tableop.get_tables(targets=[self.tname])[0]
        pk, pkidx = table.pk, table.pkidx
        rows = sorted(values[self.key_table])
        data = self.get_table_data(rows)
        pkvals = [d[pkidx] for d in data]
        # Update
        self.dbop.delete_by_pk(self.tname, pk, pkvals)
        self.dbop.commit()
        [self.table_data.pop(r - i) for i, r in enumerate(rows)]
        self.window[self.key_table].update(self.table_data)
        #
        [print(f'Delete: {list(d)}') for d in data]


class TableChangeWindow(BaseWindow):
    def __init__(self, parent, util, rows, tname, columns, selected_data, table_data, parent_loc=()):
        self.parent = parent
        self.util = util
        self.rows = rows
        self.tname = tname
        self.columns = columns
        self.selected_data = selected_data
        self.table_data = table_data

        self.prefkey = prefkey = f'_table{tname}change__.'
        self.key_update = f'{prefkey}update'
        self.key_inputs = [[f'{prefkey}{r}.{c}.input' for c in columns] for r in rows]

        layout = [
            [sg.Button('Update', **attr.base_button, button_color=attr.color_warning, key=self.key_update)],
            [sg.Text(c, **attr.base_text, size=(20, 1)) for i, c in enumerate(columns)],
            [[sg.InputText(d0d, **attr.base_inputtext, key=self.key_inputs[i][j], size=(20, 1))
              for j, d0d in enumerate(d1d)] for i, d1d in enumerate(selected_data)],
        ]

        self.window = sg.Window(
            f'EasyDBO {tname} Update',
            layout,
            size=(1200, 400),
            resizable=True,
            finalize=True,
        )

        if parent_loc:
            self.window.move(parent_loc[0], parent_loc[1] + 30)

    def handle(self, event, handle):
        if event == self.key_update:
            # Check
            if not all([self.selected_data[i] == self.table_data[r] for i, r in enumerate(self.rows)]):
                print('Error: Could not update due to data changes in table')
                self.close()
                return

            table = self.util.tableop.get_tables(targets=[self.tname])[0]
            pk, pkidx = table.pk, table.pkidx

            updates = []
            for i, keys in enumerate(self.key_inputs):
                origin = self.selected_data[i]
                update = [self.window[k].get() for k in keys]
                diff = {c: u for i, (c, o, u) in enumerate(zip(self.columns, origin, update)) if o != u}
                if not diff:
                    continue
                pkval = origin[pkidx]
                self.util.dbop.update(self.tname, diff, pk, pkval)
                updates.append(update)

            self.util.dbop.commit()
            self.parent.notify_update(self.rows, updates)
            self.close()
