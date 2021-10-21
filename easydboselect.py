from easydbo.init.argument import ArgumentSelectLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.output.table import TableOutput

arguments = ArgumentSelectLoader().get()
configs = ConfigLoader().get()
tableop = TableLoader().get()
dbop = DatabaseOperation(configs['database'])

if arguments.main == 'alias':
    from easydbo.main.select.alias import main
elif arguments.main == 'match':
    from easydbo.main.select.match import main
elif arguments.main == 'show_alias':
    from easydbo.main.select.show_alias import main
elif arguments.main == 'sql':
    from easydbo.main.select.sql import main

title, columns, rows = main(arguments, configs, tableop, dbop)
dbop.close()

res = [{}]
res[0]['title'] = title
res[0]['columns'] = columns
res[0]['select'] = rows
TableOutput.table(res)
