import json
from easydbo.table import Table
from easydbo.init.find import Finder

class TableGetter(Finder):
    def __init__(self):
        self.filename = 'table.json'

    def get(self):
        path = self.find(self.filename)
        with open(path) as f:
            tables = json.load(f)
        exl_table = [Table(t['name'], t['pk'], t['columns'],
                           t['type'], t['attr'], t['excel']) for t in tables if t['excel']]
        db_table = [Table(t['name'], t['pk'], t['columns'],
                          t['type'], t['attr'], t['excel']) for t in tables if not t['excel']]
        return exl_table, db_table
