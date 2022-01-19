from easydbo.init.alias import AliasManagerCLI
from easydbo.output.print_ import SimplePrint as SP

def main(arguments, configs, tableop, dbop):
    aliasmgr = AliasManagerCLI()

    # Check
    tgt_alias_name = arguments.name
    if not tgt_alias_name:
        SP.error('--alias option is required at this time')
    aliasmgr.check_alias_name(tgt_alias_name)

    # Access database
    dbop.authenticate()
    tgt_alias = aliasmgr.get_alias_by_name(tgt_alias_name)
    tgt_cmd = tgt_alias.query
    rows = dbop.select_by_cmd(tgt_cmd)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_query()

    return title, columns, rows
