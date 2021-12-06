import sys

def print_table_data(data2d):
    [print(list(d1d)) for d1d in data2d]
    sys.stdout.flush()

def save_table_data_as_csv(table, path, delimiter=',', show_save_message=True):
    if not path:
        return
    header = table.ColumnHeadings
    data2d = table.get()  # data2d=[(...), ...]
    with open(path, 'w') as f:
        data_str = f'{delimiter.join(header)}\n' if header else ''
        for d1 in data2d:
            data_str += delimiter.join([str(d0) for d0 in d1]) + '\n'
        f.write(data_str)
        if show_save_message:
            print(f'Save: {path}')
    sys.stdout.flush()
