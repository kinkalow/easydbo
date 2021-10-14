import re
from easydbo.output.log import Log

def main(arguments, configs, tableop, dbop):
    selects = arguments.match[0]
    conds = arguments.match[1] if len(arguments.match) > 1 else ''
    #join = arguments.match[2] if len(arguments.match) > 2 else ''

    # Convet to SQL

    # label
    tgt_labels = selects.split(',')
    if tgt_labels == '*':
        Log.error('NOT IMPLIMENTED YET')
    label_sql = ', '.join(tgt_labels)

    # join
    tgt_names_2d = tableop.get_names_by_labels(tgt_labels)
    tgt_names_1d = list(set([n for n1 in tgt_names_2d for n in n1]))
    join_sql = ' NATURAL JOIN '.join(tgt_names_1d)

    # condition
    if conds:
        pat = r'=|!=|<|>|<=|>=|&|\|'
        cond_sp = [s.strip() for s in re.split(pat, conds)]
        pat_sp = re.findall(pat, conds)
        labels = tableop.get_labels(flat=True)
        assert(len(cond_sp) - 1 == len(pat_sp))
        cond_sql = ''
        for i, p in enumerate(pat_sp):
            if p == '&':
                cond_sql += 'AND '
            elif p == '|':
                cond_sql += 'OR '
            else:
                left = cond_sp[i]
                right = cond_sp[i + 1]
                left_in_labels = left in labels
                right_in_labels = right in labels
                if left_in_labels and not right_in_labels:
                    if not re.match(r'"|\'', right[0]):
                        right = f"'{right}'"
                elif not left_in_labels and right_in_labels:
                    if not re.match(r'"|\'', left[0]):
                        left = f"'{left}'"
                elif not left_in_labels and not right_in_labels:
                    Log.error(f'Either side of operator({p}) must be label (left={left},right={right})')
                cond_sql += f'{left} {p} {right} '
        cond_sql = cond_sql.rstrip()

    sql = f'SELECT {label_sql} FROM {join_sql} WHERE {cond_sql}'

    # Access database
    dbop.authenticate()
    rows = dbop.select_by_cmd(sql)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_statement()

    return title, columns, rows
