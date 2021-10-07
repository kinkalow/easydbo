from easydbo.output.log import Log
from easydbo import constant
from datetime import datetime

class DataChecker:
    def __init__(self, idx_valid, idx_date):
        self.idx_valid = idx_valid
        self.idx_date = idx_date

    def convert(self, data):
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

    def check_unique(self, idxes, data):
        max_len = len(data)
        for idx in idxes:
            d = [d[idx] for d in data]
            if len(set(d)) != max_len:
                Log.error(f'{self.columns[idx]}(column) of {self.sheet}(sheet) must have unique elements')

    def check_null(self, idxes, data):
        for idx in idxes:
            for d in data:
                if d == constant.NAN_STR:
                    Log.error(f'{self.columns[idx]}(column) of {self.sheet}(sheet) must not be empty')
