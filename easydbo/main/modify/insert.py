from easydbo.util.hash import get_diff_idx
from easydbo.excel.data import normalize, check_data

def main(arguments, configs, tableop, dbop):
    tables = tableop.get_tables()
    tbl = tables[tableop.to_idx(arguments.table)]

    # Data to insert
    idxes_valid = tbl.get_idxes_valid()
    idxes_date = tbl.get_idxes_date()
    new_data = normalize(idxes_valid, idxes_date, arguments.fields)
    dbop.authenticate()
    check_data(dbop, tbl, new_data)

    # Get database data
    db_data = dbop.select(tbl.name, tbl.columns)

    # Get indexes with no common data
    new_diffidx = get_diff_idx(new_data, db_data)[0]

    # Set insert data
    tbl.insert = [new_data[i] for i in new_diffidx]

    # Insert data into database
    if tbl.insert:
        dbop.insert(tbl.name, tbl.columns, tbl.insert)

    return [tbl]
