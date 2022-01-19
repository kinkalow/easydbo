from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput

def gate(operation):
    if operation == 'delete':
        from easydbo.init.argument import ArgumentDeleteLoader as ArgumentLoader
        from .delete import main
    elif operation == 'excel':
        from easydbo.init.argument import ArgumentExcelLoader as ArgumentLoader
        from .excel import main
    elif operation == 'insert':
        from easydbo.init.argument import ArgumentInsertLoader as ArgumentLoader
        from .insert import main
    elif operation == 'update':
        from easydbo.init.argument import ArgumentUpdateLoader as ArgumentLoader
        from .update import main

    arguments = ArgumentLoader().get()
    configs = ConfigLoader().get()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])

    tbls = main(arguments, configs, tableop, dbop)
    #title, columns, rows = main(arguments, configs, tableop, dbop)

    dbop.commit()
    TableOutput.fulltable(tbls, dbop)
    dbop.close()

    #res = [{}]
    #res[0]['title'] = title
    #res[0]['columns'] = columns
    #res[0]['select'] = rows
    #TableOutput.table(res)
