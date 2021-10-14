from easydbo.init.argument import ArgumentLoader
from easydbo.init.config import ConfigLoader
from easydbo.init.table import TableLoader
from easydbo.database.operation import DatabaseOperation
from easydbo.excel.util import get_sheet
from easydbo.excel.operation import ExcelOperation
from easydbo.util.hash import HashCreator, HashDiff
from easydbo.output.table import TableOutput

# Load
while True:
    inp = input("Choose 'select', 'insert', 'delete', 'update': ")
    print(inp)
