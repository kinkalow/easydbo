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
        def split(str_):
            name2d = tableop.get_names()
            col2d = tableop.get_columns()

            names_cols = [s for s in re.split(r'[^\w\.]', str_) if s]
            cand_names = []
            cand_cols = []
            for nc in names_cols:
                s = nc.split(r'.')
                if len(s) == 2:
                    cand_names.append(s[0])
                    cand_cols.append(s[1])
                else:
                    cand_names.append('')
                    cand_cols.append(nc)
            for n in cand_names:
                if n and n not in name2d:
                    Log.error(f'Table "{n}" does not exst')

            names = []
            cols = []
            for i, c in enumerate(cand_cols):
                idxes = []
                for j, col1d in enumerate(col2d):
                    if c in col1d:
                        if cand_names[i]:
                            names.append(cand_names[i])
                            cols.append(cand_cols[i])
                            break
                        idxes.append(j)
                if len(idxes) == 1:
                    names.append(name2d[idxes[0]])
                    cols.append(c)
                elif len(idxes) > 1:
                    names = [name2d[i] for i, n in enumerate(name2d) if i in idxes]
                    Log.error(f'Column "{c}" requires a table name: {names}')

            return names, cols

        tgt_names1, tgt_cols1 = split(arg_cols)
        tgt_names2, tgt_cols2 = split(arg_conds)
        tgt_names = []
        tgt_cols = []
        for n, c in zip(tgt_names1 + tgt_names2, tgt_cols1 + tgt_cols2):
            for n2, c2 in zip(tgt_names, tgt_cols):
                if n == n2 and c == c2:
                    break
            else:
                tgt_names.append(n)
                tgt_cols.append(c)
        if not tgt_names:
            Log.error('Could not guess table names')
        sql_from = 'FROM ' + ' NATURAL JOIN '.join(set(tgt_names))

    # conditions
    sql_where = '' if arg_conds == '' else f'WHERE {arg_conds}'

    sql = f'{sql_select} {sql_from} {sql_where}'.strip() + ';'

    # Access database
    dbop.authenticate()
    rows = dbop.select_by_cmd(sql)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_statement()

    if not rows:
        Log.info(title)

    return title, columns, rows
