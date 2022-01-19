from easydbo.init.argument import ArgumentSelectLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput

def gate():
    arguments = ArgumentSelectLoader().get()
    configs = ConfigLoader().get()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])

    if arguments.main == 'alias':
        from .alias import main
    elif arguments.main == 'match':
        from .match import main
    elif arguments.main == 'show_alias':
        from .show_alias import main
    elif arguments.main == 'sql':
        from .sql import main

    title, columns, rows = main(arguments, configs, tableop, dbop)
    dbop.close()

    res = [{}]
    res[0]['title'] = title
    res[0]['columns'] = columns
    res[0]['select'] = rows
    TableOutput.table(res)
