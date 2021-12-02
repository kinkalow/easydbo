import re
from easydbo.output.log import Log
from easydbo.main.select.sql import execute_query

_VIEW_PREFIX = '__easydbo_tmpview'

# NOTE: This is a simple algorithm
def _guess_tables(tableop, str_):
    tname1d = tableop.get_tnames()          # Table names list
    col2d = tableop.get_columns(full=True)  # Columns list

    # Find strings of form 'table.column' or 'column'
    tnames_cols = [s for s in re.split(r'[^\w\.]', str_) if s]
    cand_tnames = []
    cand_cols = []
    for nc in tnames_cols:
        s = nc.split(r'.')
        if len(s) == 2:
            cand_tnames.append(s[0])
            cand_cols.append(s[1])
        else:
            cand_tnames.append('')
            cand_cols.append(nc)
    for n in cand_tnames:
        if n and n not in tname1d:
            Log.error(f'Table "{n}" does not exist')

    # Filter candidates
    tnames = []
    renames = []  # table.name -> name
    for i, c in enumerate(cand_cols):
        idxes = []
        for j, col1d in enumerate(col2d):
            if c in col1d:
                if cand_tnames[i]:
                    tnames.append(cand_tnames[i])
                    renames.append((f'{cand_tnames[i]}.{cand_cols[i]}', cand_cols[i]))
                    break
                idxes.append(j)
        for i in idxes:
            tnames.append(tname1d[i])

    return tnames, renames

def _sort_tables_in_join_order(tnames, tableop):
    col2d = tableop.get_columns(tnames, full=True)
    # Determine order to join
    cols = set(col2d[0])
    cands = list(range(1, len(col2d)))
    orders = [0]
    while cands:
        for cand in cands:
            if cols.intersection(col2d[cand]):
                cols = cols.union(col2d[cand])
                cands.remove(cand)
                orders.append(cand)
                break
        else:
            Log.error(f'{tnames} tables do not have common column names')
    if orders != list(range(len(col2d))):
        tnames = [tnames[i] for i in orders]
    return tnames

def _create_view_sql(tnames, tableop):
    col2d = tableop.get_columns(tnames, full=True)

    # Create column and table list for view SQL
    #from datetime import datetime
    #view_base = f"{_VIEW_PREFIX}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    view_base = _VIEW_PREFIX
    view_names = [f'{view_base}_{i}' for i in range(len(col2d) - 1)]
    view_cols = []
    for i in range(len(col2d) - 1):
        view_cols.append(col2d[0] if i == 0 else view_cols[i - 1][:])
        for c in col2d[i + 1]:
            if c not in view_cols[i]:
                view_cols[i].append(c)
    view_cols = [','.join(v) for v in view_cols]
    view_tbls = [(tnames[i], tnames[i + 1]) if i == 0 else
                 (view_names[i - 1], tnames[i + 1]) for i in range(len(col2d) - 1)]

    # Create view SQL
    sql_pre = [f'''
CREATE VIEW {view_names[i]} AS
SELECT {view_cols[i]} FROM {view_tbls[i][0]} NATURAL LEFT JOIN {view_tbls[i][1]}
UNION
SELECT {view_cols[i]} FROM {view_tbls[i][0]} NATURAL RIGHT JOIN {view_tbls[i][1]};
'''.replace('\n', ' ').strip() for i in range(len(view_cols))]
    sql_post = [f'DROP VIEW IF EXISTS {view_names[i]};' for i in range(len(view_names))]

    return sql_pre, sql_post, view_names[-1]

def _create_select_sql(sql_select, sql_from, sql_where):
    return f'{sql_select} {sql_from} {sql_where}'.strip() + ';'

def _execute_view_and_select_sqls(dbop, sql, sql_pre, sql_post):
    def del_prev_temp_view():
        dbop.execute('SHOW TABLES')
        tables = dbop.fetchall()
        for t, in tables:
            if re.match(_VIEW_PREFIX, t):
                dbop.execute(f'DROP VIEW IF EXISTS {t}')

    def on_query_error():
        for s in sql_post:
            dbop.execute(s)

    # Access database
    dbop.authenticate()
    del_prev_temp_view()
    dbop.set_query_error(on_query_error)
    try:
        for s in sql_pre:
            dbop.execute(s)
        return execute_query(dbop, sql)
    finally:
        on_query_error()
        dbop.set_query_error()

def main(arguments, configs, tableop, dbop):
    # Execute selection query
    # SELECT <columns> FROM <tables> WHERE <condtions>

    arg_cols = arguments.columns.strip()
    arg_conds = arguments.conditions.strip()
    arg_tbls = arguments.tables.strip()

    # Create select and where sql statements
    sql_select = f'SELECT {arg_cols}'
    sql_where = '' if arg_conds == '' else f'WHERE {arg_conds}'
    # Exit if table statement is specified
    if arg_tbls:
        sql_from = f'FROM {arg_tbls}' if arg_tbls else ''
        sql = _create_select_sql(sql_select, sql_from, sql_where)
        return execute_query(dbop, sql)

    if re.match(r'\*.*', arg_cols) and not arg_conds and not arg_tbls:
        # Special case
        all_tnames = tableop.get_tnames()
        if arg_cols == '*':
            tnames = all_tnames
        else:
            tnames = []
            cols = arg_cols[1:].split(',')
            for tname in cols:
                if tname not in all_tnames:
                    Log.error('{tname} table does not exist')
                if tname not in tnames:
                    tnames.append(tname)
            sql_select = 'SELECT *'
    else:
        # Guess table names
        tnames1, rename1 = _guess_tables(tableop, arg_cols)
        tnames2, rename2 = _guess_tables(tableop, arg_conds)
        tnames = tnames1 + [t for t in tnames2 if t not in tnames1]  # Remove duplicates
        for from_, to in rename1:
            sql_select = sql_select.replace(from_, to)
        for from_, to in rename2:
            sql_where = sql_where.replace(from_, to)

    # Exit if no table name
    if not tnames:
        Log.error('Could not guess table names')

    # No need to join if only one table name
    if len(tnames) == 1:
        sql_from = f'FROM {tnames[0]}'
        sql = _create_select_sql(sql_select, sql_from, sql_where)
        return execute_query(dbop, sql)

    # Create view and selection SQL and execute them
    tnames = _sort_tables_in_join_order(tnames, tableop)
    sql_pre, sql_post, final_view_name = _create_view_sql(tnames, tableop)
    sql_from = f'FROM {final_view_name}'
    sql = _create_select_sql(sql_select, sql_from, sql_where)
    return _execute_view_and_select_sqls(dbop, sql, sql_pre, sql_post)
