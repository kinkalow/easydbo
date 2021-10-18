import re
from easydbo.output.log import Log

def main(arguments, configs, tableop, dbop):
    arg_cols = arguments.match[0] if arguments.match[0] != '' else '*'
    arg_conds = arguments.match[1] if len(arguments.match) > 1 else ''
    arg_tbls = arguments.match[2] if len(arguments.match) > 2 else ''

    # Create select querry

    # columns
    sql_select = f"SELECT {arg_cols}"

    # tables
    if arg_tbls:
        sql_from = f'FROM {arg_tbls}' if arg_tbls else ''
    else:
        from easydbo.util.util import flat
        col2d = tableop.get_columns()
        pat = r'\W'
        #
        candidate_cols = [s for s in re.split(pat, arg_conds) if s]
        idxes = sorted(list({i for c in candidate_cols for i, col1d in enumerate(col2d) if c in col1d}))
        guess_names = tableop.get_names_by_idxes(idxes) if idxes else []
        guess_cols = list(set(flat(tableop.get_columns(inculde_names=guess_names))))
        #
        candidate_cols = [s for s in re.split(pat, arg_cols) if s]
        cols = sorted(list({c for c in candidate_cols for col1d in col2d if c in col1d}))
        add_tbls = [c for c in cols if c not in guess_cols]
        #
        guess_names += tableop.get_names_by_columns(add_tbls)
        if not guess_names:
            Log.error('Could not guess table names')
        sql_from = 'FROM ' + ' NATURAL JOIN '.join(guess_names)

    # conditions
    sql_where = '' if arg_conds == '' else f'WHERE {arg_conds}'

    sql = f'{sql_select} {sql_from} {sql_where}'

    # Access database
    dbop.authenticate()
    rows = dbop.select_by_cmd(sql)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_statement()

    return title, columns, rows
