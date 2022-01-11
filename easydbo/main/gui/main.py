from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.main.gui.window.application import Application
from easydbo.init.alias import AliasLoader


def main():
    configs = ConfigLoader().get()
    aliases = AliasLoader().get()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])
    dbop.authenticate()
    app = Application(configs, aliases, tableop, dbop)
    app.loop()
