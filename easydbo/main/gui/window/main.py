import re
import functools
import PySimpleGUI as sg
from easydbo.exception import EASYDBO_GOTO_LOOP, EASYDBO_USER_ERROR
from easydbo.output.log import Log
from .base import BaseWindow, SubWindowManager
from .alias import AliasWindow
from .table import TableWindow
from .common.layout.attribution import Attribution as attr
from .common.sql import create_sql_result


class MainWindow(BaseWindow):
    def __init__(self, util):
        super().__init__(util.winmgr)
        self.util = util
        tnames = util.tnames

        prefkey = '_main__.'
        self.key_tables = [f'{prefkey}{t}' for t in tnames]
        self.key_alias = f'{prefkey}alias'
        self.key_excel = f'{prefkey}excel'

        # Layout
        self.fulljoin = FullJoinLayout(prefkey, util)
        layout = [
            [sg.Button(f' {tn} ', **attr.base_button_with_color_warning, key=self.key_tables[i]) for i, tn in enumerate(util.tnames)],
            [sg.Button(' Alias ', **attr.base_button_with_color_safety, key=self.key_alias),
             sg.Button(' Excel ', **attr.base_button_with_color_warning, key=self.key_excel)],
            [sg.Text('')],
            [self.fulljoin.layout],
        ]

        # Windows
        self._window = sg.Window(
            'EasyDBO Main',
            layout,
            location=(5000, 200),
            size=(1300, 800),
            resizable=True,
            finalize=True,
        )
        # Subwindows
        subwin_names = self.key_tables + [self.key_alias]
        self.subwinmgr = SubWindowManager(util.winmgr, self.window, subwin_names)
        # Add window objects to fulljoin layout
        self.fulljoin.set_window(self.window, self.subwinmgr)

    def handle(self, event, values):
        if event in self.key_tables:
            self.open_table(event)
        elif event in self.key_alias:
            self.alias(event)
        elif event in self.key_excel:
            pass
        else:
            self.fulljoin.handle(event, values)

    def open_table(self, key):
        tname = key.split('.')[-1]
        location = self.subwinmgr.get_location(dy=80)
        self.subwinmgr.create_single_window(key, TableWindow, tname, self.util, location)

    def alias(self, key, location=None, size=None):
        # NOTE: This method is also invoked in AliasWindow class
        #     : location and size arugements are defined in AliasWindow class
        if not location:
            location = self.subwinmgr.get_location(widgetkey=self.key_alias, widgety=True, dy=60)
        alias_method = functools.partial(self.alias, key)
        self.subwinmgr.create_single_window(key, AliasWindow, self.util, location, alias_method, size=size)


class FullJoinLayout():
    def __init__(self, prefkey, util):
        self.util = util

        self.tableop = util.tableop
        self.dbop = util.dbop

        self.prefkey = prefkey
        self.key_cols_cbs = [[f'{prefkey}{t}.{c}.checkbox' for c in util.fullcolumns[i]] for i, t in enumerate(util.tnames)]
        self.key_cols_conds = [[f'{prefkey}{t}.{c}.inputtext' for c in util.fullcolumns[i]] for i, t in enumerate(util.tnames)]
        self.key_show = f'{prefkey}show'
        self.key_checkall = f'{prefkey}checkall'
        self.key_checkclear = f'{prefkey}checkclear'
        self.key_inputtextclear = f'{prefkey}inputtextclear'
        self.key_select = f'{prefkey}select'
        self.key_from = f'{prefkey}from'
        self.key_where = f'{prefkey}where'
        self.key_others = f'{prefkey}otheres'
        self.key_create = f'{prefkey}create'
        self.key_query = f'{prefkey}query'

        # Full Outer Join
        tnames_columns = []
        for i, tn in enumerate(util.tnames):
            tnames_columns.append([
                sg.Text(f' {tn} ', **attr.text_table, size=(len(tn) + 2, 1)),
            ])
            tnames_columns.append([
                sg.Checkbox(c, key=self.key_cols_cbs[i][j], **attr.base_checkbox, size=(20 - 3, 1))
                for j, c in enumerate(util.fullcolumns[i])
            ])
            tnames_columns.append([
                sg.InputText('', key=self.key_cols_conds[i][j], **attr.base_inputtext, size=(20, 1))
                for j, c in enumerate(util.fullcolumns[i])
            ])
        join_frame = sg.Frame(
            '', tnames_columns,
            key=None, border_width=5,
            title_location=sg.TITLE_LOCATION_TOP,
            title_color='#49d665', font=('', 15, 'bold'),
        )

        layout = [[join_frame]]
        layout += [
            [
                sg.Button('Show', **attr.base_button_with_color_safety, key=self.key_show),
                sg.Frame(
                    'Check',
                    [[
                        sg.Button('All', **attr.base_button_with_color_safety, key=self.key_checkall),
                        sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_checkclear),
                    ]],
                    title_location=sg.TITLE_LOCATION_LEFT,
                ),
                sg.Frame(
                    'Text',
                    [[
                        sg.Button('Clear', **attr.base_button_with_color_safety, key=self.key_inputtextclear),
                    ]],
                    title_location=sg.TITLE_LOCATION_LEFT,
                )
            ],
            [sg.Text('')],
            [
                sg.Text('SELECT', **attr.base_text, size=(7, 1)),
                sg.InputText('', **attr.base_inputtext, key=self.key_select, expand_x=True),
            ],
            [
                sg.Text('FROM', **attr.base_text, size=(7, 1)),
                sg.InputText('', **attr.base_inputtext, key=self.key_from, expand_x=True),
            ],
            [
                sg.Text('WHERE', **attr.base_text, size=(7, 1)),
                sg.InputText('', key=self.key_where, **attr.base_inputtext, expand_x=True),
            ],
            [
                sg.Text('', **attr.base_text, size=(7, 1)),
                sg.InputText('', key=self.key_others, **attr.base_inputtext, expand_x=True),
            ],
            [
                sg.Button('Create', **attr.base_button_with_color_safety, key=self.key_create),
                sg.Button('Query', **attr.base_button_with_color_safety, key=self.key_query),
            ],
        ]

        self.layout = layout

    #def bind(self, window):
    #    pass
    #    [window[k].bind('<Leave>', f'{k}.focusout-') for k1 in self.key_cols_cbs for k in k1]
    #    [window[k].bind('<Leave>', f'{k}.focusout-') for k1 in self.key_cols_conds for k in k1]

    def set_window(self, window, subwinmgr):
        self.window = window
        self.subwinmgr = subwinmgr

    def handle(self, event, values):
        values_rmv = {k: v for k, v in values.items()
                      if isinstance(k, str) and k.startswith(self.prefkey)}
        if event == self.key_show:
            self.show(*self.create_query(values_rmv))
        elif event == self.key_checkall:
            self.check_checkboxes(values_rmv, True)
        elif event == self.key_checkclear:
            self.check_checkboxes(values_rmv, False)
        elif event == self.key_inputtextclear:
            self.input_text_clear(values_rmv)
        elif event == self.key_create:
            self.create_clause(values_rmv)
        elif event == self.key_query:
            self.query(values_rmv)

    def create_query(self, values):
        # Create SELECT clause from checkboxes
        cbs = [k for k, v in values.items() if k.endswith('.checkbox') and v]  # k='prefkey.table.column.suffix'
        cb_tbls = [c.split('.')[1] for c in cbs]
        cb_cols = [c.split('.')[2] for c in cbs]
        sql_select = _create_select_clause(cb_cols)

        # Do nothing if none of checkboxes are selected
        if not cbs:
            raise EASYDBO_GOTO_LOOP('Checkboxes are not selected.')

        # Create WHERE clause from input texts
        inputs = [(k, v) for k, v in values.items()
                  if k.endswith('.inputtext') and v]
        inp_tbls = [i[0].split('.')[1] for i in inputs]
        inp_cols = [i[0].split('.')[2] for i in inputs]
        inp_conds = [i[1] for i in inputs]
        sql_where = _create_where_clause(inp_tbls, inp_cols, inp_conds)

        # Create FROM clause from checkboxes and input texts
        sql_from = _create_from_clause(self.tableop, cb_tbls, inp_tbls)

        # Result
        return sql_select, sql_from, sql_where

    def show(self, sql_select, sql_from, sql_where, sql_others=''):
        # Query
        query = f'{sql_select} {sql_from} {sql_where} {sql_others}'.rstrip() + ';'
        location = self.subwinmgr.get_location(dy=30)
        create_sql_result(query, self.util, self.subwinmgr, location)
        #return
        #ret = self.dbop.execute(query, ignore_error=True)
        #if ret.is_error:
        #    return
        #header = self.dbop.get_current_columns()
        #data = self.dbop.fetchall()

        # Print data on new window
        #location = self.subwinmgr.get_location(dy=30)
        #self.subwinmgr.create_window(QueryResultWindow, self.util, query, header, data, location)

    def check_checkboxes(self, values, true_or_false):
        for k in values.keys():
            if k.endswith('.checkbox'):
                self.window[k].Update(value=true_or_false)

    def input_text_clear(self, values):
        for k in values.keys():
            if k.endswith('.inputtext'):
                self.window[k].Update(value='')

    def create_clause(self, values):
        sql_select, sql_from, sql_where = self.create_query(values)
        sql_select = re.sub('^SELECT', '', sql_select).strip()
        sql_from = re.sub('^FROM', '', sql_from).strip()
        sql_where = re.sub('^WHERE', '', sql_where).strip()
        self.window[self.key_select].Update(value=sql_select)
        self.window[self.key_from].Update(value=sql_from)
        self.window[self.key_where].Update(value=sql_where)

    def query(self, values):
        sql_select = values[self.key_select].strip()
        sql_from = values[self.key_from].strip()
        sql_where = values[self.key_where].strip()
        sql_others = values[self.key_others].strip()
        sql_select = f'SELECT {sql_select}' if sql_select else ''
        sql_from = f'FROM {sql_from}' if sql_from else ''
        sql_where = f'WHERE {sql_where}' if sql_where else ''
        if sql_select:
            self.show(sql_select, sql_from, sql_where, sql_others=sql_others)

#
# Create sql
#

def _create_select_clause(cb_cols):
    return 'SELECT ' + ', '.join(cb_cols)

def _parse_condition(column, condition):
    try:
        cond_fmt = re.sub(r'\*+', '{}', re.sub('[^&|]', '*', condition))  # '1&2|3' ---> '{}|{}|{}'
        conds = re.split('[&|]', condition)
        news = []
        add_err_msg = ''
        range_eq = {
            r'\[([^\[\{]+):([^\]\}]+)\]$': ['>=', '<='],  # '=[1:3]' ---> 'column >= 1 AND column <= 3'
            r'\[([^\[\{]+):([^\]\}]+)\}$': ['>=', '<'],   # '=[1:3}' ---> 'column >= 1 AND column <  3'
            r'\{([^\[\{]+):([^\]\}]+)\]$': ['>', '<='],   # '={1:3]' ---> 'column >  1 AND column <= 3'
            r'\{([^\[\{]+):([^\]\}]+)\}$': ['>', '<'],    # '={1:3}' ---> 'column >  1 AND column <  3'
        }
        for i, c in enumerate(conds):
            c_fmt = re.sub(r'\*+', '{}', re.sub('[^()]', '*', c))  # '(=1)' ---> '({})'
            tgt = c.replace('(', '').replace(')', '')
            if tgt.startswith('=[') or tgt.startswith('={') \
            or tgt.startswith('![') or tgt.startswith('!{') \
            or tgt.startswith('[') or tgt.startswith('{'):
                is_eq = False if tgt.startswith('![') or tgt.startswith('!{') else True
                tgt_trim = tgt[1:] \
                    if tgt.startswith('=[') or tgt.startswith('={') \
                    or tgt.startswith('![') or tgt.startswith('!{') \
                    else tgt
                for p, (left, right) in range_eq.items():
                    m = re.match(p, tgt_trim)
                    if m:
                        if is_eq:
                            op = 'AND'
                        else:
                            left = '<' if left == '>=' else '<='
                            right = '>' if right == '<=' else '>='
                            op = 'OR'
                        new = f'{column} {left} "{m.group(1)}" {op} {column} {right} "{m.group(2)}"'
                        break
                else:
                    add_err_msg = 'Format: "[:]", "[:}", "{:]", "{:}"'
                    raise EASYDBO_USER_ERROR
            elif tgt.startswith('='):
                new = f'{column} = "{tgt[1:]}"'
            elif tgt.startswith('!'):
                new = f'{column} <> "{tgt[1:]}"'
            elif tgt.startswith('<='):
                new = f'{column} <= "{tgt[2:]}"'
            elif tgt.startswith('<'):
                new = f'{column} < "{tgt[1:]}"'
            elif tgt.startswith('>='):
                new = f'{column} >= "{tgt[2:]}"'
            elif tgt.startswith('>'):
                new = f'{column} > "{tgt[1:]}"'
            else:
                new = f'{column} = "{tgt}"'
                #add_err_msg = 'Missing symbol: "=", "!", "<=", "<", ">=", ">", "[", "{"'
                #raise EASYDBO_USER_ERROR
            news.append(c_fmt.format(f'({new})'))
        return cond_fmt.format(*news)
    except EASYDBO_USER_ERROR:
        msg = f'Invalid condition "{condition}" in "{column}"'
        msg += f'\n{add_err_msg}' if add_err_msg else ''
        raise EASYDBO_GOTO_LOOP(msg)

def _create_where_clause(inp_tbls, inp_cols, inp_conds):
    if not inp_tbls:
        return ''
    conds = []
    for t, c, cond_str in zip(inp_tbls, inp_cols, inp_conds):
        cond_str = _parse_condition(c, cond_str)
        conds.append(cond_str)
    return 'WHERE ' + ' AND '.join(conds)

def _check_common_column(tnames, tableop):
    columns = tableop.get_columns(tnames, full=True)
    sets = set(columns[0])
    for i in range(1, len(tnames)):
        s = set(columns[i])
        sets = sets.intersection(s)
        if len(sets) == 0:
            Log.error(f'"{tnames[i-1]}" and "{tnames[i]}" have no common column')

def _create_from_clause(tableop, cb_tbls, inp_tbls):
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
