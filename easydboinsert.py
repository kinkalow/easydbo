from easydbo.init.argument import ArgumentInsertLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.hash import get_diff_idx
from easydbo.output.table import TableOutput

# Loaders
arg_loader = ArgumentInsertLoader()
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


# Data to insert
new_data = arguments.fields

# Get database data
db_columns = [tbl.pk] + tbl.columns if tbl.pkidx == -1 else tbl.columns
db_data = dbop.select(tbl.name, db_columns)
if tbl.pkidx == -1:
    db_data_pk = [d.pop(0) for d in db_data]  # Pop primary values
else:
    db_data_pk = [d[tbl.pkidx] for d in db_data]

# Get indexes with no common data
new_diffidx = get_diff_idx(new_data, db_data)[0]

# Set insert data
tbl.insert = [new_data[i] for i in new_diffidx]

# Insert data into database
if tbl.insert:
    dbop.insert(tbl.name, tbl.columns, tbl.insert)


# Close
dbop.commit()
dbop.close()
# Output
TableOutput.table(tbls)
