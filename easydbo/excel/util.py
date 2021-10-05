import openpyxl

def get_sheet(path):
    return openpyxl.load_workbook(path).sheetnames
