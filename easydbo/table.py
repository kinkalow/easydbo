class Table:
    def __init__(self, name, pk, columns_info):
        self.name = name
        self.pk = pk
        self.columns, self.type, self.attr = self._split_colinfo(columns_info)
        #
        self.pkidx = self.name_to_idx(pk)
        self.auto_pk = self._get_auto_pk_info(self.pkidx, pk)
        self.attr = self._add_pk_to_attr(self.pkidx, self.attr)
        self.attr_null = self._attr_null(self.attr)
        self.attr_unique = self._attr_unique(self.attr)
        #
        self._insert = []
        self._delete = []
        self._delete_by_pk = []

    # for initial functions --->

    def _split_colinfo(self, columns_info):
        columns = list(columns_info.keys())
        type_ = [c[0] for c in columns_info.values()]
        attr = [c[1] for c in columns_info.values()]
        return columns, type_, attr

    def _get_auto_pk_info(self, pkidx, pk):
        return {
            'columns': pkidx,
            'type': 'INTEGER UNSIGNED',
            'attr': 'PRIMARY KEY AUTO INCREMENT'
        } if pkidx == -1 and pk else {}

    def _add_pk_to_attr(self, pkidx, attr):
        if pkidx != -1 and 'PRIMARY KEY' not in attr[pkidx]:
            space = ' ' if len(attr[pkidx]) > 0 else ''
            attr[pkidx] = f'PRIMARY KEY{space}{attr[pkidx]}'
        return attr

    def _attr_null(self, attr):
        return [False if 'NOT NULL' in a or 'PRIMARY KEY' in a else True for a in attr]

    def _attr_unique(self, attr):
        return [True if 'UNIQUE' in a or 'PRIMARY KEY' in a else False for a in attr]

    # <---

    def get_column_date(self):
        return [self.columns[i] for i, t in enumerate(self.type) if t == 'DATE']

    def get_idx_null(self):
        return [i for i, t_or_f in enumerate(self.attr_null) if t_or_f]

    def get_idx_uniq(self):
        return [i for i, t_or_f in enumerate(self.attr_unique) if t_or_f]

    def name_to_idx(self, name):
        try:
            return self.columns.index(name)
        except ValueError:
            return -1
        return self.columns.index(name)

    # ---

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
