import json
from easydbo.init.file import File
from easydbo.output.log import Log

class AliasLoader(File):
    def __init__(self):
        self.filename = 'alias.json'
        self.aliases = self._load()

    def _load(self):
        path = self.find(self.filename)
        with open(path) as f:
            aliases = json.load(f)
        return [Alias(a['name'], a['sql']) for a in aliases]

    def get_aliasnames(self):
        return [a.name for a in self.aliases]

    def get_idx_by_name(self, name):
        return self.get_aliasnames().index(name)

    def get_alias_by_name(self, name):
        return self.aliases[self.get_idx_by_name(name)]

    def check_alias_name(self, name):
        if name not in self.get_aliasnames():
            Log.error(f"Alias must be chosen from list: {self.get_aliasnames()}")

    def get(self):
        return self.aliases


class Alias:
    def __init__(self, name, sql):
        self.name = name
        self.sql = sql
