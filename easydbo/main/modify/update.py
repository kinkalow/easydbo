from easydbo.excel.data import normalize, check_data

def main(arguments, configs, tableop, dbop):
    tables = tableop.get_tables()
    tbl = tables[tableop.to_idx(arguments.table)]
    dbop.authenticate()

    # Target
    tgt_pairs = arguments.pairs
    tgt_cols = tgt_pairs.keys()
    tbl.has_columns(tgt_cols)
    tgt_pk = arguments.pk
    tgt_table = arguments.table
    tgt_where = f'{tbl.pk}="{tgt_pk}"'
    org_data = dbop.select(tgt_table, tbl.columns, where=tgt_where)[0]
    tgt_data = [[tgt_pairs[c] if c in tgt_cols else org_data[i] for i, c in enumerate(tbl.columns)]]

    # Check data to update
    idxes_valid = tbl.get_idxes_valid()
    idxes_date = tbl.get_idxes_date()
    new_data = normalize(idxes_valid, idxes_date, tgt_data)
    except_idxes = [i for i, c in enumerate(tbl.columns) if c not in tgt_cols]
    check_data(dbop, tbl, new_data, except_idxes)

    # Update
    dbop.update(arguments.table, tgt_pairs, tbl.pk, tgt_pk)
    tbl.update_by_pk = [tgt_pk]
    tbl.update = new_data

    return [tbl]
