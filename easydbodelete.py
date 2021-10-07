from easydbo.init.argument import ArgumentDeleteLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput

# Loaders
arg_loader = ArgumentDeleteLoader()
cfg_loader = ConfigLoader()
tbl_loader = TableLoader()
arguments = arg_loader.get()
configs = cfg_loader.get()
tables = tbl_loader.get()
# Database
dbop = DatabaseOperation(configs['database'])
dbop.authenticate()
# Tables
tbl = tables[tbl_loader.to_idx(arguments.table)]
tbls = [tbl]


# Get database data
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


# Last
dbop.commit()
TableOutput.fulltable(tbls, dbop)
dbop.close()
