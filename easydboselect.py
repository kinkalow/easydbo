from easydbo.init.argument import ArgumentSelectLoader
from easydbo.init.config import ConfigLoader
#from easydbo.init.table import TableLoader
from easydbo.init.alias import AliasLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput

# Loaders
arg_loader = ArgumentSelectLoader()
cfg_loader = ConfigLoader()
#tbl_loader = TableLoader()
alias_loader = AliasLoader()
arguments = arg_loader.get()
configs = cfg_loader.get()
#tables = tbl_loader.get()


# Show alias and commands
if arguments.show_alias:
    aliases = alias_loader.get()
    names = [a.name for a in aliases]
    sqls = [a.sql for a in aliases]
    out = [{}]
    out[0]['title'] = ''
    out[0]['columns'] = ['Alias', 'SQL']
    out[0]['select'] = list(zip(names, sqls))
    TableOutput.table(out)
    exit()


# Check
tgt_alias_name = arguments.alias_name
if not tgt_alias_name:
    print('--alias option is required at this time')
    exit()
alias_loader.check_alias_name(tgt_alias_name)

# Database
dbop = DatabaseOperation(configs['database'])
dbop.authenticate()
tgt_alias = alias_loader.get_alias_by_name(tgt_alias_name)
tgt_cmd = tgt_alias.sql
tgt_res = dbop.select_by_cmd(tgt_cmd)
tgt_cols = dbop.get_current_columns()
tgt_stmt = dbop.get_current_statement()

# Set output
out = [{}]
out[0]['title'] = tgt_stmt
out[0]['columns'] = tgt_cols
out[0]['select'] = tgt_res


# Last
dbop.commit()
TableOutput.table(out)
dbop.close()
