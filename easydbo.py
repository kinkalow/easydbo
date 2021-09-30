from easydbo.init.argument import ArgumentGetter
from easydbo.init.config import ConfigGetter
from easydbo.init.table import TableGetter
from easydbo.database.operation import DatabaseOperation
from easydbo.excel.operation import ExcelOperation
from easydbo.hash import HashCreator, HashDiff
from easydbo.output import Output
#from easydbo.database.manager import DatabaseManager
#from easydbo.excel.manager import ExcelManager
#from easydbo.table import column
#from easydbo.excel import sheetname
#from easydbo import compare_hash
#from easydbo.table import table

# Initial settings
arggeter = ArgumentGetter()
cfggeter = ConfigGetter()
tblgeter = TableGetter()
args = arggeter.get()
cfgs = cfggeter.get()
tblexl, tbldb = tblgeter.get()

exl_path = args.excel_path
db_cfg = cfgs['database']
exl_cfg = cfgs['excel']
#exlmgr = ExcelManager()
dbop = DatabaseOperation(db_cfg)
dbop.authenticate()
hash_creator = HashCreator()

# Get data to insert or delte
for idx_tblexl in range(len(tblexl)):
    tblexl_i = tblexl[idx_tblexl]
    table = tblexl_i.name
    columns = tblexl_i.columns
    primary_key = tblexl_i.pk
    primary_idx = tblexl_i.pkidx
    db_columns = [primary_key] + columns if primary_idx == -1 else columns

    # Get all column elements in excel sheet
    exlop = ExcelOperation(exl_cfg, exl_path, table, columns, primary_idx)
    exl_data = exlop.get_data()
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
    tblexl_i.insert = [exl_data[i] for i in exl_diffidx]
    tblexl_i.delete = [db_data[i] for i in db_diffidx]
    tblexl_i.delete_by_pk = [db_data_pk[i] for i in db_diffidx]

#print(data)
#print('-' * 10)
#print(dbop.select('human', ['*']))
#print(dbop.select('cancer', ['*']))
#exit()

for idx_tblexl in range(len(tblexl)):
    tblexl_i = tblexl[idx_tblexl]
    sheet = tblexl_i.name
    columns = tblexl_i.columns
    if tblexl_i.delete_by_pk:
        dbop.delete_by_pk(sheet, tblexl_i.pk, tblexl_i.delete_by_pk)
    if tblexl_i.insert:
        dbop.insert(sheet, columns, tblexl_i.insert)

#print('-' * 10)
#print(dbop.select('human', ['*']))
#print(dbop.select('cancer', ['*']))
#exit()


dbop.commit()
dbop.close()


#cfg.ver
Output.prettyprint(tblexl)
