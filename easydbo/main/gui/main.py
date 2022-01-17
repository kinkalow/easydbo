from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.init.alias import AliasManager
from .application import Application


def main():
    configs = ConfigLoader().get()
    aliasmgr = AliasManager()
    tableop = TableLoader().get()
    dbop = DatabaseOperation(configs['database'])
    dbop.authenticate()
    app = Application(configs, aliasmgr, tableop, dbop)
    app.loop()
