import re
from easydbo.output.log import Log
from easydbo.main.select.sql import execute_query

def main(arguments, configs, tableop, dbop):
    arg_cols = arguments.columns
    arg_conds = arguments.conditions
    arg_tbls = arguments.tables

    #if re.match(r'\*.+', arg_cols):
    #    tables = ' NATURAL JOIN '.join([s.strip() for s in arg_cols[1:].split(',')])
    #    sql = f'SELECT * FROM {tables};'

    # Create selection querry
    # SELECT <columns> FROM <tables> WHERE <condtions>

    # Create sql columns
    sql_select = f'SELECT {arg_cols}'

    # Create sql tables
    if arg_tbls:
        sql_from = f'FROM {arg_tbls}' if arg_tbls else ''

    else:
        # Determine tables from arg_cols and arg_tbls
        # NOTE: This is a simple algorithm

        def get_tnames_columns(str_):
            tname2d = tableop.get_tnames()  # Table names list
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
                if n and n not in tname2d:
                    Log.error(f'Table "{n}" does not exist')

            # Check if the candidates found above are correct
            tnames = []
            cols = []
            for i, c in enumerate(cand_cols):
                idxes = []
                for j, col1d in enumerate(col2d):
                    if c in col1d:
                        if cand_tnames[i]:
                            tnames.append(cand_tnames[i])
                            cols.append(cand_cols[i])
                            break
                        idxes.append(j)
                if len(idxes) == 1:
                    tnames.append(tname2d[idxes[0]])
                    cols.append(c)
                elif len(idxes) > 1:
                    tnames = [tname2d[i] for i, n in enumerate(tname2d) if i in idxes]
                    Log.error(f'Column "{c}" requires a table name: {tnames}')

            return tnames, cols

        # Table names and columns
        tgt_tnames1, tgt_cols1 = get_tnames_columns(arg_cols)
        tgt_tnames2, tgt_cols2 = get_tnames_columns(arg_conds)
        # Remove duplicates
        tgt_tnames = []
        tgt_cols = []
        for n, c in zip(tgt_tnames1 + tgt_tnames2, tgt_cols1 + tgt_cols2):
            for n2, c2 in zip(tgt_tnames, tgt_cols):
                if n == n2 and c == c2:
                    break
            else:
                tgt_tnames.append(n)
                tgt_cols.append(c)
        # Exit if no table name
        if not tgt_tnames:
            Log.error('Could not guess table names')
        # Join all tables
        sql_from = 'FROM ' + ' NATURAL JOIN '.join(set(tgt_tnames))

    # Create sql conditions
    sql_where = '' if arg_conds == '' else f'WHERE {arg_conds}'

    sql = f'{sql_select} {sql_from} {sql_where}'.strip() + ';'

    # Access database
    return execute_query(dbop, sql)
    #dbop.authenticate()
    #rows = dbop.select_by_cmd(sql)  # Perform this method first
    #columns = dbop.get_current_columns()
    #title = dbop.get_current_statement()

    #if not rows:
    #    Log.info(title)

    #return title, columns, rows
