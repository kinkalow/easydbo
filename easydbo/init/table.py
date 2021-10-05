import json
from easydbo.table import Table
from easydbo.init.file import File
from easydbo.output.log import Log

class TableLoader(File):
    def __init__(self):
        self.filename = 'table.json'
        self.tables = self._load()

    def _load(self):
        path = self.find(self.filename)
        with open(path) as f:
            tables = json.load(f)
        return [Table(t['name'], t['pk'], t['columns']) for t in tables]

    def get(self):
        return self.tables

    def to_idx(self, target):
        names = [t.name for t in self.tables]
        idx = names.index(target)
        if idx == -1:
            Log.error(f'Sheet name must be one of the following: {names}')
        return idx
