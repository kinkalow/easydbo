import functools
import PySimpleGUI as sg
import re
from easydbo.exception import EASYDBO_GOTO_LOOP, EASYDBO_USER_ERROR
from .alias import AliasWindow
from .base import BaseWindow
from .common.layout.attribution import Attribution as attr
from .common.popup import popup_error
from .common.sql import create_query_result_window
from .common.util import get_location
from .table import TableWindow
from ..manager import SubWindow


class MainWindow(BaseWindow):
    def __init__(self, pack):
        self.pack = pack
        tnames = pack.tableop.get_tnames()

        prefkey = self.make_prefix_key('main')
        self.key_tables = [f'{prefkey}{t}' for t in tnames]
        self.key_alias = f'{prefkey}alias'
        self.key_excel = f'{prefkey}excel'

        # Layout
        self.fulljoin = FullJoinLayout(prefkey, pack)
        layout = [
            [sg.Button(f' {tn} ', **attr.base_button_with_color_warning, key=self.key_tables[i]) for i, tn in enumerate(tnames)],
            [sg.Button(' Alias ', **attr.base_button_with_color_safety, key=self.key_alias),
             sg.Button(' Excel ', **attr.base_button_with_color_warning, key=self.key_excel)],
            [sg.Text('')],
            [self.fulljoin.layout],
        ]

        # Windows
        self._window = sg.Window(
            'EasyDBO Main',
            layout,
            finalize=True,
            location=(5000, 200),
            resizable=True,
            size=(1300, 800),
        )
        # Subwindows
        subwin_names = self.key_tables + [self.key_alias]
        self.subwin = SubWindow(self.window, subwin_names)
        # Add window objects to fulljoin layout
        self.fulljoin.set_window(self.window, self.subwin)

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
        location = get_location(self.window, dy=80)
        self.subwin.create_unique(key, TableWindow, tname, self.pack, location)

    def alias(self, key, location=None, size=None):
        # NOTE: This method is also invoked in AliasWindow class
        #     : location and size arugements are defined in AliasWindow class
        if not location:
            location = get_location(self.window, keyy=self.key_alias, dy=80)
        alias_method = functools.partial(self.alias, key)
        self.subwin.create_unique(key, AliasWindow, self.pack, location, alias_method, size=size)


class FullJoinLayout():
    def __init__(self, prefkey, pack):
        self.pack = pack

        self.tableop = pack.tableop
        self.dbop = pack.dbop
        tnames = pack.tableop.get_tnames()
        fullcolumns = pack.tableop.get_columns(full=True)

        self.prefkey = prefkey
        self.key_cols_cbs = [[f'{prefkey}{t}.{c}.checkbox' for c in fullcolumns[i]] for i, t in enumerate(tnames)]
        self.key_cols_conds = [[f'{prefkey}{t}.{c}.inputtext' for c in fullcolumns[i]] for i, t in enumerate(tnames)]
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
        for i, tn in enumerate(tnames):
            tnames_columns.append([
                sg.Text(f' {tn} ', **attr.text_table, size=(len(tn) + 2, 1)),
            ])
            tnames_columns.append([
                sg.Checkbox(c, key=self.key_cols_cbs[i][j], **attr.base_checkbox, size=(20 - 3, 1))
                for j, c in enumerate(fullcolumns[i])
            ])
            tnames_columns.append([
                sg.InputText('', key=self.key_cols_conds[i][j], **attr.base_inputtext, size=(20, 1))
                for j, c in enumerate(fullcolumns[i])
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

    def set_window(self, window, subwin):
        self.window = window
        self.subwin = subwin

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

    def create_query(self, values, key=None):
        # Do nothing if none of checkboxes are selected
        cbs = [k for k, v in values.items() if k.endswith('.checkbox') and v]  # k='prefkey.table.column.suffix'
        if not cbs:
            popup_error('No checkbox selected', get_location(self.window, key=key if key else self.key_show))

        # Processing relating to selected checkboxes and inputted texts
        cb_tbls = [c.split('.')[1] for c in cbs]
        cb_cols = [c.split('.')[2] for c in cbs]
        inputs = [(k, v) for k, v in values.items() if k.endswith('.inputtext') and v]
        inp_tbls = [i[0].split('.')[1] for i in inputs]
        inp_cols = [i[0].split('.')[2] for i in inputs]
        inp_conds = [i[1] for i in inputs]

        # Create required table names
        tnames = set([t for t in cb_tbls + inp_tbls])
        tnames = [t for t in self.tableop.get_tnames() if t in tnames]  # Sort

        # Create sql
        same_cols = self.tableop.get_same_column_names()
        sql_select = _create_select_clause(tnames, cb_tbls, cb_cols, same_cols)
        sql_where = _create_where_clause(tnames, inp_tbls, inp_cols, inp_conds, same_cols)
        sql_from = _create_from_clause(self.tableop, tnames, cb_tbls, inp_tbls)

        # Result
        return sql_select, sql_from, sql_where

    def show(self, sql_select, sql_from, sql_where, sql_others=''):
        query = f'{sql_select} {sql_from} {sql_where} {sql_others}'.rstrip() + ';'
        location = get_location(self.window, dy=30)
        create_query_result_window(query, self.pack, self.subwin, location)

    def check_checkboxes(self, values, true_or_false):
        for k in values.keys():
            if k.endswith('.checkbox'):
                self.window[k].Update(value=true_or_false)

    def input_text_clear(self, values):
        for k in values.keys():
            if k.endswith('.inputtext'):
                self.window[k].Update(value='')

    def create_clause(self, values):
        sql_select, sql_from, sql_where = self.create_query(values, key=self.key_create)
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
        if sql_select or (not sql_select and not sql_from and not sql_where and sql_others):
            self.show(sql_select, sql_from, sql_where, sql_others=sql_others)

#
# Create sql
#

# ---> select clause

def _renames_columns_for_select(tbls, cols, coms, need_as):
    if need_as:
        return [f'{t}.{c} AS {t}${c}' if c in coms else c for t, c in zip(tbls, cols)]
    else:
        return [f'{t}${c}' if c in coms else c for t, c in zip(tbls, cols)]

def _create_select_clause(tnames, cb_tbls, cb_cols, same_cols):
    cols = _renames_columns_for_select(cb_tbls, cb_cols, same_cols, len(tnames) == 1)
    return 'SELECT ' + ', '.join(cols)

# <--- select clause
# ---> where clause

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

def _renames_columns_for_where(tbls, cols, coms, use_dot):
    dot_or_dollar = '.' if use_dot else '$'
    return [f'{t}{dot_or_dollar}{c}' if c in coms else c for t, c in zip(tbls, cols)]

def _create_where_clause(tnames, inp_tbls, inp_cols, inp_conds, same_cols):
    if not inp_tbls:
        return ''
    re_inp_cols = _renames_columns_for_where(inp_tbls, inp_cols, same_cols, len(tnames) == 1)
    conds = []
    for t, c, cond_str in zip(inp_tbls, re_inp_cols, inp_conds):
        cond_str = _parse_condition(c, cond_str)
        conds.append(cond_str)
    return 'WHERE ' + ' AND '.join(conds)

# <--- where clause
# ---> from clause

def _get_same_column_names(tableop, tnames):
    '''
    Params
        tableop:          : Table operation object
        tnames : List[Str]: Table names with two or more elements
    Return
        same_cols: List[List[Str]]:  Column names with the same names in each table
    '''
    columns = tableop.get_columns(tnames, full=True)
    same_cols = []
    sets = set(columns[0])
    for i in range(1, len(tnames)):
        s = set(columns[i])
        sets = sets.intersection(s)
        if len(sets) == 0:
            raise EASYDBO_GOTO_LOOP(f'"{tnames[i-1]}" and "{tnames[i]}" have no common column')
        same_cols.append(list(sets))
    return same_cols

def _create_subquery_columns(tableop, tnames):
    '''
    Params
        tableop:          : Table operation object
        tnames : List[Str]: Table names with two or more elements
    Return
        sel_cols: List[Str]: column names for subquery SELECT clause
    '''
    same_cols = _get_same_column_names(tableop, tnames)
    columns_l = tableop.get_columns([tnames[0]], full=True)[0]
    columns_r = tableop.get_columns([tnames[1]], full=True)[0]
    renames_l = [f'{tnames[0]}.{c} AS {tnames[0]}${c}' if c in same_cols[0] else c for i, c in enumerate(columns_l)]
    renames_r = [f'{tnames[1]}.{c} AS {tnames[1]}${c}' if c in same_cols[0] else c for i, c in enumerate(columns_r)]
    sel_cols = [', '.join(renames_l + renames_r)]
    if len(tnames) == 2:
        return sel_cols
    nexts_l = [f'{tnames[0]}${c}' if c in same_cols[0] else c for i, c in enumerate(columns_l)]
    nexts_r = [f'{tnames[1]}${c}' if c in same_cols[0] else c for i, c in enumerate(columns_r)]
    next_str = ', '.join(nexts_l + nexts_r)
    for it in range(2, len(tnames)):
        columns = tableop.get_columns([tnames[it]], full=True)[0]
        renames = [f'{tnames[it]}.{c} AS {tnames[it]}${c}' if c in same_cols[it - 1] else c for c in columns]
        columns_str = next_str + ', ' + ', '.join(renames)
        sel_cols.append(columns_str)
        if it != len(tnames) - 1:
            nexts = [f'{tnames[it]}${c}' if c in same_cols[it - 1] else c for c in columns]
            next_str += ', ' + ', '.join(nexts)
    for i in range(len(same_cols) - 1):
        sel_cols[i] += ', ' + ', '.join(same_cols[i])
    return sel_cols


def _create_from_clause(tableop, tnames, cb_tbls, inp_tbls):
    if len(tnames) == 1:
        sql_from = f'FROM {tnames[0]}'
    else:
        columns = _create_subquery_columns(tableop, tnames)
        subquery = ''
        for i in range(len(tnames) - 1):
            table_l, table_r = (tnames[0], tnames[1]) if i == 0 else (tnames[1 + i], subquery)
            subquery = f'''
(SELECT {columns[i]} FROM {table_l} NATURAL LEFT JOIN {table_r}
UNION
SELECT {columns[i]} FROM {table_l} NATURAL RIGHT JOIN {table_r})_
'''.strip()
        sql_from = 'FROM ' + subquery.replace('\n', ' ')
    return sql_from
