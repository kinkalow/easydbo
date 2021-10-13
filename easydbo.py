from easydbo.init.argument import ArgumentLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.excel.util import get_sheet
from easydbo.excel.operation import ExcelOperation
from easydbo.util.hash import HashCreator, HashDiff
from easydbo.output.table import TableOutput

# Load
while True:
    inp = input("Choose 'select', 'insert', 'delete', 'update': ")
    print(inp)


arg_loader = ArgumentLoader()
cfg_loader = ConfigLoader()
tbl_loader = TableLoader()
arguments = arg_loader.get()
configs = cfg_loader.get()
tables = tbl_loader.get()

# Configs
db_cfg = configs['database']
exl_cfg = configs['excel']

# All tables
exl_path = arguments.excel_path
sheets = get_sheet(exl_path)
tblexls = [tables[tbl_loader.to_idx(sheet)] for sheet in sheets]

dbop = DatabaseOperation(db_cfg)
dbop.authenticate()

hash_creator = HashCreator()

# Get data to insert or delte
for tblexl in tblexls:
    table = tblexl.name
    type_ = tblexl.type
    columns = tblexl.columns
    primary_key = tblexl.pk
    primary_idx = tblexl.pkidx
    idxes_col_uniq = [i for i, t_or_f in enumerate(tblexl.attr_unique) if t_or_f]
    idxes_col_null = [i for i, t_or_f in enumerate(tblexl.attr_null) if t_or_f]

    # Get all column elements in excel sheet
    exlop = ExcelOperation(exl_cfg, exl_path, tblexl)
    exlop.check_unique(idxes_col_uniq)
    exlop.check_null(idxes_col_null)
    exl_data = exlop.get_data()

    db_columns = [primary_key] + columns if primary_idx == -1 else columns
    t_db_data = dbop.select(table, db_columns)
    if primary_idx == -1:
        db_data_pk = [d.pop(0) for d in t_db_data]  # Pop primary values
        db_data = t_db_data
    else:
        db_data_pk = [d[primary_idx] for d in t_db_data]
        db_data = t_db_data

    # Calculates hash values for each row in excel and database and
    # prints the difference
    exl_hash = hash_creator.create(exl_data)
    db_hash = hash_creator.create(db_data)
    exl_diffidx, db_diffidx = HashDiff(exl_hash, db_hash).get_noncom_idx()

    # Set data to insert or delete in database
    tblexl.insert = [exl_data[i] for i in exl_diffidx]
    tblexl.delete = [db_data[i] for i in db_diffidx]
    tblexl.delete_by_pk = [db_data_pk[i] for i in db_diffidx]

#print(data)
#print('-' * 10)
#print(dbop.select('human', ['*']))
#print(dbop.select('cancer', ['*']))
#exit()

for tblexl in tblexls:
    sheet = tblexl.name
    columns = tblexl.columns
    if tblexl.delete_by_pk:
        dbop.delete_by_pk(sheet, tblexl.pk, tblexl.delete_by_pk)
    if tblexl.insert:
        dbop.insert(sheet, columns, tblexl.insert)

#print('-' * 10)
#print(dbop.select('human', ['*']))
#print(dbop.select('cancer', ['*']))
#exit()

dbop.commit()
dbop.close()

TableOutput.table(tblexls)
