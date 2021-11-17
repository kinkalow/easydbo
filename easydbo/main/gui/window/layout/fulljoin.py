import PySimpleGUI as sg
from .base import BaseLayout
from .common import Attribution as attr
from ..select_result import SelectResultWindow

class FullJoinTab(BaseLayout):
    def __init__(self, winmgr, prefkey, util):
        self.winmgr = winmgr
        self.util = util

        self.tableop = util.tableop
        self.dbop = util.dbop
        self.prefkey = prefkey

        self.key_cols_cbs = [[f'{prefkey}{t}.{c}.checkbox' for c in util.fullcolumns[i]]
                             for i, t in enumerate(util.tnames)]
        self.key_cols_conds = [[f'{prefkey}{t}.{c}.inputtext' for c in util.fullcolumns[i]]
                               for i, t in enumerate(util.tnames)]
        self.key_show = f'{prefkey}show'
        self.key_clear = f'{prefkey}clear'
        self.key_create = f'{prefkey}create'
        self.key_save = f'{prefkey}save'
        self.key_select = f'{prefkey}select'
        self.key_where = f'{prefkey}where'
        self.key_query = f'{prefkey}query'
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

    def handle(self, event, values):
        event_rmv = self.remove_prefix_key(self.prefkey, event)
        if event_rmv == 'show':
            v = self.filter_values_by_prefix_key(self.prefkey, values)
            self.show(event, v)

    def run(self, event, values):
        action = event[1:-1].split('.')[1]
        if action == 'show':
            self.remove_prefix_key()
            self.show(event, values)

    def show(self, event, values):
        #values['_fulljoin__.human.center_name.checkbox'] = True
        #values['_fulljoin__.human.project_name.checkbox'] = True
        #values['_fulljoin__.human.human_cancer_type.checkbox'] = True
        #values['_fulljoin__.cancer.cancer_receive_date.inputtext'] = '>2021-01-01'

        # Create SELECT clause from checkboxes
        cbs = [k for k, v in values.items()
               if k.endswith('.checkbox') and v]  # k='prefkey.table.column.suffix'
        cb_tbls = [c.split('.')[1] for c in cbs]
        cb_cols = [c.split('.')[2] for c in cbs]
        sql_select = _create_select_clause(cb_cols)

        # Create WHERE clause from input texts
        inputs = [(k, v) for k, v in values.items()
                  if k.endswith('.inputtext') and v]
        inp_tbls = [i[0].split('.')[1] for i in inputs]
        inp_cols = [i[0].split('.')[2] for i in inputs]
        inp_conds = [i[1] for i in inputs]
        sql_where = _create_where_clause(inp_tbls, inp_cols, inp_conds)

        # Create FROM clause from checkboxes and input texts
        sql_from = _create_from_clause(self.tableop, cb_tbls, inp_tbls)

        # Query
        sql = f'{sql_select} {sql_from} {sql_where}'.rstrip() + ';'
        from easydbo.main.select.sql import execute_query
        query, headings, data = execute_query(self.dbop, sql)

        # Print data on new Window
        self.make_result_window(query, headings, data)

    def make_result_window(self, query, headings, data):
        win = SelectResultWindow(self.winmgr, self.util, query, headings, data)
        self.winmgr.add_window(win)

def _create_select_clause(cb_cols):
    tables = ', '.join(cb_cols) if cb_cols else '*'
    return f'SELECT {tables}'

def _create_where_clause(inp_tbls, inp_cols, inp_conds):
    if not inp_tbls:
        return ''
    conds = []
    for t, c, cond1l in zip(inp_tbls, inp_cols, inp_conds):
        for cond in cond1l.split(','):
            if not cond:
                continue
            condition = f'({c}{cond})'
            conds.append(condition)
    return 'WHERE ' + 'AND '.join(conds)

def _check_common_column(tnames, tableop):
    columns = tableop.get_columns(tnames, full=True)
    sets = set(columns[0])
    for i in range(1, len(tnames)):
        s = set(columns[i])
        sets = sets.intersection(s)
        if len(sets) == 0:
            from easydbo.output.log import Log
            Log.error(f'"{tnames[i-1]}" and "{tnames[i]}" have no common column')

def _create_from_clause(tableop, cb_tbls, inp_tbls):
    if not cb_tbls and not inp_tbls:
        tnames = tableop.get_tnames()
    else:
        tnames = set([t for t in cb_tbls + inp_tbls])
        tnames = [t for t in tableop.get_tnames() if t in tnames]  # Sort

    if len(tnames) == 1:
        sql_from = f'FROM {tnames[0]}'

    else:
        _check_common_column(tnames, tableop)
        columns = subquery = ''
        for i in range(len(tnames) - 1):
            if i == 0:
                column_l = tableop.get_columns([tnames[0]], full=True)[0]
                column_r = tableop.get_columns([tnames[1]], full=True)[0]
                table_l, table_r = tnames[0], tnames[1]
            else:
                column_l = columns
                column_r = tableop.get_columns([tnames[i + 1]], full=True)[0]
                table_l, table_r = tnames[1 + i], subquery
            columns = column_l + [c for c in column_r if c not in column_l]
            columns_str = ', '.join(columns)
            subquery = f'''
(SELECT {columns_str} FROM {table_l} NATURAL LEFT JOIN {table_r}
UNION
SELECT {columns_str} FROM {table_l} NATURAL RIGHT JOIN {table_r})_
'''.strip()
        sql_from = 'FROM ' + subquery.replace('\n', ' ')

    return sql_from
