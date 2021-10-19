from easydbo.init.alias import AliasLoader
from easydbo.output.log import Log

def main(arguments, configs, tableop, dbop):
    alias_loader = AliasLoader()

    # Check
    tgt_alias_name = arguments.alias
    if not tgt_alias_name:
        Log.error('--alias option is required at this time')
    alias_loader.check_alias_name(tgt_alias_name)

    # Access database
    dbop.authenticate()
    tgt_alias = alias_loader.get_alias_by_name(tgt_alias_name)
    tgt_cmd = tgt_alias.sql
    rows = dbop.select_by_cmd(tgt_cmd)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_statement()

    return title, columns, rows
