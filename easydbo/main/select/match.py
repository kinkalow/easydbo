import re
from easydbo.output.log import Log
from easydbo.main.select.sql import execute_query

def _create_sql(sql_select, sql_from, sql_where):
    return f'{sql_select} {sql_from} {sql_where}'.strip() + ';'

def main(arguments, configs, tableop, dbop):
    arg_cols = arguments.columns.strip()
    arg_conds = arguments.conditions.strip()
    arg_tbls = arguments.tables.strip()

    #if re.match(r'\*.+', arg_cols):
    #    tables = ' NATURAL JOIN '.join([s.strip() for s in arg_cols[1:].split(',')])
    #    sql = f'SELECT * FROM {tables};'

    # Create selection query
    # SELECT <columns> FROM <tables> WHERE <condtions>

    sql_pre = []
    sql_post = []

    # Create sql columns
    sql_select = f'SELECT {arg_cols}'

    # Create sql conditions
    sql_where = '' if arg_conds == '' else f'WHERE {arg_conds}'

    # Create sql tables
    if arg_tbls:
        sql_from = f'FROM {arg_tbls}' if arg_tbls else ''
        sql = _create_sql(sql_select, sql_from, sql_where)
        return execute_query(dbop, sql)

    else:
        # Determine tables from arg_cols and arg_tbls
        # NOTE: This is a simple algorithm

        def get_tnames_columns(str_):
            tname1d = tableop.get_tnames()  # Table names list
            col2d = tableop.get_columns()   # columns list

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
            #cols = []
            for i, c in enumerate(cand_cols):
                idxes = []
                for j, col1d in enumerate(col2d):
                    if c in col1d:
                        if cand_tnames[i]:
                            tnames.append(cand_tnames[i])
                            #cols.append(cand_cols[i])
                            renames.append((f'{cand_tnames[i]}.{cand_cols[i]}', cand_cols[i]))
                            break
                        idxes.append(j)
                for i in idxes:
                    tnames.append(tname1d[i])
                    #cols.append(c)

            return tnames, renames

        # Table names and columns
        tnames1, rename1 = get_tnames_columns(arg_cols)
        tnames2, rename2 = get_tnames_columns(arg_conds)

        # Remove duplicates
        tgt_tnames = list(set(tnames1 + tnames2))

        # Exit if no table name
        if not tgt_tnames:
            Log.error('Could not guess table names')

        if len(tgt_tnames) == 1:
            sql_from = f'FROM {tgt_tnames[0]}'
            sql = _create_sql(sql_select, sql_from, sql_where)
            return execute_query(dbop, sql)

        # If there are multiple target tables, perform full outer join

        # Determine order to join
        t_col2d = tableop.get_columns(tgt_tnames)
        cols = set(t_col2d[0])
        cands = list(range(1, len(t_col2d)))
        orders = [0]
        while cands:
            for cand in cands:
                if cols.intersection(t_col2d[cand]):
                    cols = cols.union(t_col2d[cand])
                    cands.remove(cand)
                    orders.append(cand)
                    break
            else:
                Log.error(f'{tgt_tnames} tables do not have common column names')
        if orders != list(range(len(t_col2d))):
            tgt_tnames = [tgt_tnames[i] for i in orders]
            t_col2d = tableop.get_columns(tgt_tnames)

        # Create view columns and tables
        from datetime import datetime
        view_name_base = f"easydbo_tmpview_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        view_names = [f'{view_name_base}_{i}' for i in range(len(t_col2d) - 1)]
        view_cols = []
        for i in range(len(t_col2d) - 1):
            view_cols.append(t_col2d[0] if i == 0 else view_cols[i - 1][:])
            for c in t_col2d[i + 1]:
                if c not in view_cols[i]:
                    view_cols[i].append(c)
        view_cols = [','.join(v) for v in view_cols]
        view_tbls = [(tgt_tnames[i], tgt_tnames[i + 1]) if i == 0 else
                     (view_names[i - 1], tgt_tnames[i + 1]) for i in range(len(t_col2d) - 1)]

        # Create view SQL
        sql_pre = [f'''
CREATE VIEW {view_names[i]} AS
SELECT {view_cols[i]} FROM {view_tbls[i][0]} NATURAL LEFT JOIN {view_tbls[i][1]}
UNION
SELECT {view_cols[i]} FROM {view_tbls[i][0]} NATURAL RIGHT JOIN {view_tbls[i][1]};
'''.replace('\n', ' ').strip() for i in range(len(view_cols))]
        sql_post = [f'DROP VIEW IF EXISTS {view_names[i]};' for i in range(len(view_names))]

        # Create selection SQL
        sql_from = f'FROM {view_names[-1]}'
        for f, t in rename1:
            sql_select = sql_select.replace(f, t)
        for f, t in rename2:
            sql_where = sql_where.replace(f, t)
        sql = _create_sql(sql_select, sql_from, sql_where)

        # Access database
        def on_query_error():
            for s in sql_post:
                dbop.execute(s)
        dbop.authenticate()
        dbop.set_query_error_func(on_query_error)
        try:
            for s in sql_pre:
                dbop.execute(s)
            return execute_query(dbop, sql)
        finally:
            on_query_error()
            dbop.set_query_error_func()
