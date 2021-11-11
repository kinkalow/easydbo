from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.main.gui.window.window import WindowManger
from easydbo.init.alias import AliasLoader

def main():
    configs = ConfigLoader().get()
    alias = AliasLoader().get()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])
    dbop.authenticate()
    app = WindowManger(configs, alias, tableop, dbop)
    app.run()
