import openpyxl
from easydbo import constant

class ExcelOperation:
    def __init__(self, config, excel_path, sheet, columns, primary_idx):
        self.config = config
        self.excel_path = excel_path
        self.sheet = sheet
        self.columns = columns
        self.primary_idx = primary_idx

        self.data = self._load()  # self.data[row][column]
        self._check()

    def _load(self):
        wb = openpyxl.load_workbook(self.excel_path)
        sheetnum = wb.sheetnames.index(self.sheet)
        ws = wb.worksheets[sheetnum]
        data = []
        for row in ws.iter_rows(min_row=2):
            datum = []
            is_nan = True
            for cell in row:
                value = cell.value
                if value is None:
                    value = constant.NAN_STR
                else:
                    is_nan = False
                if cell.is_date:
                    value = str(value.strftime('%Y-%m-%d'))
                elif not isinstance(value, str):
                    value = str(value)
                datum.append(value)
            if not is_nan:
                data.append(datum)
        return data

    def _check(self):
        if self.primary_idx == -1:
            return
        # Check if primary_idx elements are unique
        pk_vals = [d[self.primary_idx] for d in self.data]
        if len(set(pk_vals)) != len(pk_vals):
            print('[Error] primary key values are not unique')
            exit(1)

    def get_data(self):
        return self.data

    def col_to_idx(self, cols):
        return [self.columns.index(c) for c in cols]

    def select(self, cols):
        col_idx = self.col_to_idx(cols)
        data = [[d[i] for i in col_idx] for d in self.data]
        return data
