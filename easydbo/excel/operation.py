import openpyxl
from easydbo import constant
from easydbo.output.log import Log


class ExcelOperation:
    def __init__(self, config, excel_path, sheet, columns, primary_idx):
        self.config = config
        self.excel_path = excel_path
        self.sheet = sheet
        self.columns = columns
        self.primary_idx = primary_idx
        #
        self.data = self._load()  # self.data[row][column]

    def _load(self):
        wb = openpyxl.load_workbook(self.excel_path)
        sheetnum = wb.sheetnames.index(self.sheet)
        ws = wb.worksheets[sheetnum]
        # Header
        idx_valid = []
        for row in ws.iter_rows(min_row=1, max_row=1):
            for idx, cell in enumerate(row):
                if cell.value in self.columns:
                    idx_valid.append(idx)
        if len(set(idx_valid)) != len(idx_valid):
            Log.error(f'Duplicate column names exist in {self.sheet}(sheet)')
        # Data
        data = []
        for row in ws.iter_rows(min_row=2):
            datum = []
            is_empty_row = True
            for idx in idx_valid:
                cell = row[idx]
                value = cell.value
                if value is None:
                    value = constant.NAN_STR
                else:
                    is_empty_row = False
                if cell.is_date:
                    value = str(value.strftime('%Y-%m-%d'))
                elif not isinstance(value, str):
                    value = str(value)
                datum.append(value)
            if not is_empty_row:
                data.append(datum)
        return data

    def check_unique(self, idxes):
        max_len = len(self.data)
        for idx in idxes:
            d = [d[idx] for d in self.data]
            if len(set(d)) != max_len:
                Log.error(f'{self.columns[idx]}(column) of {self.sheet}(sheet) must have unique elements')

    def check_null(self, idxes):
        for idx in idxes:
            for d in self.data:
                if d == constant.NAN_STR:
                    Log.error(f'{self.columns[idx]}(column) of {self.sheet}(sheet) must not be empty')

    def col_to_idx(self, cols):
        return [self.columns.index(c) for c in cols]

    def get_data(self):
        return self.data

    def select(self, cols):
        col_idx = self.col_to_idx(cols)
        data = [[d[i] for i in col_idx] for d in self.data]
        return data
