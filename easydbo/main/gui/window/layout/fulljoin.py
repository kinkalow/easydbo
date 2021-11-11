import PySimpleGUI as sg
from .base import BaseLayout
from .common import Attribution as attr

class FullJoinTab(BaseLayout):
    def __init__(self, winmgr, prefkey, util):
        self.winmgr = winmgr
        self.tableop = util.tableop
        self.dbop = util.dbop
        self.prefkey = prefkey

        self.key_cols_cbs = [[f'{prefkey}.{t}.{c}.checkbox' for c in util.fullcolumns[i]]
                             for i, t in enumerate(util.tnames)]
        self.key_cols_conds = [[f'{prefkey}.{t}.{c}.inputtext' for c in util.fullcolumns[i]]
                               for i, t in enumerate(util.tnames)]
        self.key_show = f'{prefkey}.show'
        self.key_clear = f'{prefkey}.clear'
        self.key_create = f'{prefkey}.create'
        self.key_save = f'{prefkey}.save'
        self.key_select = f'{prefkey}.select'
        self.key_where = f'{prefkey}.where'
        self.key_query = f'{prefkey}.query'
        #
        self.key_frame = 'key_frame'

        attr_checkbox = {'font': ('', 12)}
        attr_text = {'font': ('', 12)}
        attr_inputtext = {'font': ('', 12)}
        attr_button = {'font': ('', 12)}

        # Full Outer Join
        #max_table_length = max([len(tn) for tn in util.tnames])
        tnames_columns = []
        for i, tn in enumerate(util.tnames):
            tnames_columns.append([
                sg.Text(f' {tn} ', **attr.text_table, size=(len(tn) + 2, 1)),
            ])
            tnames_columns.append([
                sg.Checkbox(c, key=self.key_cols_cbs[i][j], **attr_checkbox, size=(20 - 3, 1))
                for j, c in enumerate(util.fullcolumns[i])
            ])
            tnames_columns.append([
                sg.InputText('', key=self.key_cols_conds[i][j], **attr_inputtext, size=(20, 1))
                for j, c in enumerate(util.fullcolumns[i])
            ])
        #
        #tnames_columns.append([
        #    sg.Frame('', [[
        #        sg.Radio('full join', 'table_join', default=True, font=_C.font13),
        #        sg.Radio('inner join', 'table_join', font=_C.font13),
        #    ]]),
        #    sg.Frame('', [[
        #        sg.Radio('AND', 'column_join', default=True, font=_C.font13),
        #        sg.Radio('OR', 'column_join', font=_C.font13),
        #    ]]),
        #])
        #
        join_frame = sg.Frame(
            '', tnames_columns,
            key=self.key_frame, border_width=5,
            title_location=sg.TITLE_LOCATION_TOP,
            title_color='#49d665', font=('', 15, 'bold'),
        )

        layout = [[join_frame]]
        layout += [
            [
                sg.Button('Show', **attr_button, key=self.key_show),
                sg.Button('Clear', **attr_button, key=self.key_clear),
                sg.Button('Create', **attr_button, key=self.key_create),
                sg.Button('Save', **attr_button, key=self.key_save),
            ],
            [
                sg.Text('SELECT', **attr_text, size=(7, 1)),
                sg.InputText('*', key=self.key_select, expand_x=True),
            ],
            [
                sg.Text('WHERE', **attr_text, size=(7, 1)),
                sg.InputText('', key=self.key_where, expand_x=True),
            ],
            [
                sg.Button('Query', **attr_button, key=self.key_query),
            ],
        ]

        self.layout = layout

    #def bind(self, window):
    #    pass
    #    [window[k].bind('<Leave>', f'{k}.focusout-') for k1 in self.key_cols_cbs for k in k1]
    #    [window[k].bind('<Leave>', f'{k}.focusout-') for k1 in self.key_cols_conds for k in k1]

    def get_layout(self):
        return self.layout

    def run(self, event, values):
        action = event[1:-1].split('.')[1]
        if action == 'show':
            self.show(event, values)

    def show(self, event, values):
        values['_fulljoin__.cancer.cancer_receive_date.checkbox'] = True
        values['_fulljoin__.cancer.cancer_receive_date.inputtext'] = '>2021-01-01'

        values = [(k, v) for k, v in values.items()
                  if isinstance(k, str) and k.startswith(f'{self.prefkey}.')]
        checks = [k for k, v in values
                  if k.endswith('.checkbox') and v]  # k='prefkey.table.column.suffix'
        chk_cols = [c.split('.')[2] for c in checks]

        inputs = [(k, v) for k, v in values
                  if k.endswith('.inputtext') and v]
        inp_tbls = [i[0].split('.')[1] for i in inputs]
        inp_cols = [i[0].split('.')[2] for i in inputs]
        inp_conds = [i[1] for i in inputs]

        from easydbo.main.select import match

        class Namespace:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)

        sel_cols = ', '.join(chk_cols) if chk_cols else '*'
        sel_conds = []
        for t, c, conds in zip(inp_tbls, inp_cols, inp_conds):
            for cs in conds.split(','):
                if not cs:
                    continue
                cond = f'{t}.{c}{cs}'
                sel_conds.append(cond)
        sel_conds = ', '.join(sel_conds)
        arguments = Namespace(columns=sel_cols, conditions=sel_conds, tables='')
        configs = ''
        title, columns, rows = match.main(arguments, configs, self.tableop, self.dbop)
        create_window(self.winmgr, title, columns, rows)

        #cmd = f'SELECT * FROM {table};'
        #data = self.dbop.execute(cmd, ret=True)
        #headings = self.tableop.get_columns(targets=[table])[0]
        #params = {
        #    'cmd': cmd,
        #    'data': data,
        #    'headings': headings,
        #}
        #win = ShowWindow(**params)
        #self.windows.append(win)
        #win()


def create_window(winmgr, cmd, headings, data):
    from .show import ShowWindow
    win = ShowWindow(cmd=cmd, headings=headings, data=data)
    winmgr.add_window(win)
    win()
