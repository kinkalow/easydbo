import json
from easydbo.table import Table
from easydbo.init.file import File

class TableGetter(File):
    def __init__(self):
        self.filename = 'table.json'

    def get(self):
        path = self.find(self.filename)
        with open(path) as f:
            tables = json.load(f)
        tables = [Table(t['name'], t['pk'], t['columns']) for t in tables]
        return tables
