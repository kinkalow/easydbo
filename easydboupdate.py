from easydbo.init.argument import ArgumentUpdateLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput
from easydbo.excel.data import normalize, check_data

# Loaders
arg_loader = ArgumentUpdateLoader()
cfg_loader = ConfigLoader()
tableop = TableLoader().get()
arguments = arg_loader.get()
configs = cfg_loader.get()
tables = tableop.get_tables()
# Database
dbop = DatabaseOperation(configs['database'])
dbop.authenticate()
# Tables
tbl = tables[tableop.to_idx(arguments.table)]
tbls = [tbl]


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


# Last
dbop.commit()
TableOutput.fulltable(tbls, dbop)
dbop.close()
