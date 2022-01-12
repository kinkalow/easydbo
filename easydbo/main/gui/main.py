from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.init.alias import AliasLoader
from .application import Application


def main():
    configs = ConfigLoader().get()
    aliases = AliasLoader().get()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])
    dbop.authenticate()
    app = Application(configs, aliases, tableop, dbop)
    app.loop()
