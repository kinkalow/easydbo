def main(arguments, configs, tableop, dbop):
    tables = tableop.get_tables()
    tbl = tables[tableop.to_idx(arguments.table)]

    # Get database data
    dbop.authenticate()
    db_columns = [tbl.pk] + tbl.columns if tbl.pkidx == -1 else tbl.columns
    db_data = dbop.select(tbl.name, db_columns)
    if tbl.pkidx == -1:
        db_data_pk = [d.pop(0) for d in db_data]  # Pop primary values
    else:
        db_data_pk = [d[tbl.pkidx] for d in db_data]

    # Get primary keys to delete
    db_diffidx = [db_data_pk.index(pk) for pk in arguments.pks if pk in db_data_pk]

    # Set delete data
    tbl.delete = [db_data[i] for i in db_diffidx]
    tbl.delete_by_pk = [db_data_pk[i] for i in db_diffidx]

    # Delete data from database
    if tbl.delete_by_pk:
        dbop.delete_by_pk(tbl.name, tbl.pk, tbl.delete_by_pk)

    return [tbl]
