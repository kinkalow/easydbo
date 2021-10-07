from easydbo.output.log import Log
from easydbo import constant
from datetime import datetime

class NewData:
    def __init__(self, idx_valid, idx_date, dbop=None):
        self.idx_valid = idx_valid
        self.idx_date = idx_date
        self.dbop = dbop

    def normalize(self, data):
        new_data = []
        is_empty_row = True
        for idx in self.idx_valid:
            value = data[idx]
            if value is None:
                value = constant.NAN_STR
            else:
                is_empty_row = False
                if idx in self.idx_date:
                    if not isinstance(value, datetime):
                        try:
                            value = datetime.strptime(value, constant.DATE_FORMAT)
                        except ValueError:
                            Log.error(f'"{value}" must be changed to match the following format "{constant.DATE_FORMAT}"')
                    value = str(value.strftime(constant.DATE_FORMAT))
                elif not isinstance(value, str):
                    value = str(value)
            new_data.append(value)
        return None if is_empty_row else new_data

class NewDataChecker:
    def __init__(self, dbop):
        self.dbop = dbop

    def unique(self, table, new_data):
        name = table.name
        idxes_uniq = table.get_idxes_uniq()
        cols_uniq = table.get_cols_uniq()
        if not idxes_uniq:
            return
        vals_uniq = self.dbop.select(name, cols_uniq)
        for idx, col in zip(idxes_uniq, cols_uniq):
            targets = [v[idx] for v in vals_uniq]
            if new_data[idx] in targets:
                Log.error(f'"{col}={new_data[idx]}" must be unique')

    def null(self, table, new_data):
        idxes_null = table.get_idxes_null()
        for i, d in enumerate(new_data):
            if i in idxes_null:
                continue
            if d == constant.NAN_STR:
                Log.error(f'"{table.columns[i]}" filed must not be null')
