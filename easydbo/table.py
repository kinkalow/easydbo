class Table:
    def __init__(self, name, pk, columns, type_, attr, excel):
        self.name = name
        self.pk = pk
        self.columns = columns
        self.type = type_
        self.attr = attr
        self.excel = excel
        #
        self.pkidx = self.name_to_idx(pk)
        self._insert = []
        self._delete = []
        self._delete_by_pk = []

    def name_to_idx(self, name):
        try:
            return self.columns.index(name)
        except ValueError:
            return -1
        return self.columns.index(name)

    @property
    def insert(self):
        return self._insert

    @insert.setter
    def insert(self, data):
        self._insert = data

    @property
    def delete(self):
        return self._delete

    @delete.setter
    def delete(self, data):
        self._delete = data

    @property
    def delete_by_pk(self):
        return self._delete_by_pk

    @delete_by_pk.setter
    def delete_by_pk(self, data):
        self._delete_by_pk = data
