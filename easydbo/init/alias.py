import json
import os
from easydbo.init.file import File
from easydbo.output.print_ import SimplePrint as SP


class AliasLoader(File):
    def __init__(self):
        filename = 'alias.json'
        self._path = self.find(filename)
        self.load()

    def load(self):
        with open(self._path) as f:
            aliases = json.load(f)
        self._aliases = [Alias(a['name'], a['query']) for a in aliases]

    def get(self):
        return self._aliases


class Alias:
    def __init__(self, name, query):
        self.name = name
        self.query = query


#
# For CLI
#
class AliasManagerCLI(AliasLoader):

    def __init__(self):
        super().__init__()

    def _get_aliasnames(self):
        return [a.name for a in self._aliases]

    def _get_idx_by_name(self, name):
        return self._get_aliasnames().index(name)

    def get_alias_by_name(self, name):
        return self._aliases[self._get_idx_by_name(name)]

    def check_alias_name(self, name):
        if name not in self._get_aliasnames():
            SP.error(f'Alias must be chosen from list: {self._get_aliasnames()}')


#
# For GUI
#
class AliasManager(AliasLoader):

    def __init__(self):
        super().__init__()
        self._update_modified_time()
        self.phconv = AliasPlaceholderConverter()

    # Modified time of alias file --->

    def _update_modified_time(self):
        self._modified_time = os.path.getmtime(self._path)

    def is_modified(self):
        return os.path.getmtime(self._path) != self._modified_time

    # <---

    def index(self, name):
        for i, a in enumerate(self._aliases):
            if name == a.name:
                return i
        return -1

    def insert(self, index, name, query):
        self._aliases.insert(index, Alias(name, query))

    def reload(self):
        if self.is_modified():
            self.load()
            self._update_modified_time()
        return self.get()

    def save(self):
        with open(self._path, 'w') as f:
            items = [{'name': a.name, 'query': a.query} for a in self._aliases]
            json.dump(items, f, indent=2)

    def update(self, name, query, index=None):
        if index:
            self._aliases[index] = Alias(name, query)
        else:
            for i, a in enumerate(self._aliases):
                if name == a.name:
                    self._aliases[i] = Alias(name, query)
                    break


class AliasPlaceholderConverter():
    def __init__(self):
        self.mark = '?'

    def count(self, query):
        return query.count(self.mark)

    def convert(self, query, values):
        for v in values:
            query = query.replace(self.mark, v, 1)
        return query

    @ property
    def placeholder_mark(self):
        return self.mark
