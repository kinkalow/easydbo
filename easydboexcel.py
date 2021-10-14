from easydbo.init.argument import ArgumentLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.util.hash import get_diff_idx
from easydbo.output.table import TableOutput
from easydbo.excel.util import get_sheet
from easydbo.excel.operation import ExcelOperation

# Loaders
arg_loader = ArgumentLoader()
cfg_loader = ConfigLoader()
tableop = TableLoader().get()
arguments = arg_loader.get()
configs = cfg_loader.get()
tables = tableop.get_tables()
# Database
dbop = DatabaseOperation(configs['database'])
dbop.authenticate()
# Tables
exl_path = arguments.excel_path
sheets = get_sheet(exl_path)
tbls = [tables[tableop.to_idx(sheet)] for sheet in sheets]


# Get data to insert or delte
for tbl in tbls:
    # Get column fields in excel sheet
    exlop = ExcelOperation(configs['excel'], exl_path, tbl)
    exlop.check_unique(tbl.get_idxes_uniq())
    exlop.check_null(tbl.get_idxes_null())
    new_data = exlop.get_data()

    # Get database data
    db_columns = [tbl.pk] + tbl.columns if tbl.pkidx == -1 else tbl.columns
    db_data = dbop.select(tbl.name, db_columns)
    if tbl.pkidx == -1:
        db_data_pk = [d.pop(0) for d in db_data]  # Pop primary values
    else:
        db_data_pk = [d[tbl.pkidx] for d in db_data]

    # Get indexes with no common data
    new_diffidx, db_diffidx = get_diff_idx(new_data, db_data)

    # Set insert and delete data
    tbl.insert = [new_data[i] for i in new_diffidx]
    tbl.delete = [db_data[i] for i in db_diffidx]
    tbl.delete_by_pk = [db_data_pk[i] for i in db_diffidx]

# Insert data into or delete data from database
for tbl in tbls:
    if tbl.delete_by_pk:
        dbop.delete_by_pk(tbl.name, tbl.pk, tbl.delete_by_pk)
    if tbl.insert:
        dbop.insert(tbl.name, tbl.columns, tbl.insert)


# Last
dbop.commit()
TableOutput.fulltable(tbls, dbop)
dbop.close()
