import subprocess
import sys
import tempfile

def print_table_data(data2d):
    [print(list(d1d)) for d1d in data2d]
    sys.stdout.flush()

def save_table_data(path, column1d, data2d, delimiter=',', show_save_message=True):
    if not path:
        return
    with open(path, 'w') as f:
        data_str = f'{delimiter.join(column1d)}\n' if column1d else ''
        for d1 in data2d:
            data_str += delimiter.join([str(d0) for d0 in d1]) + '\n'
        f.write(data_str)
        if show_save_message:
            print(f'Save: {path}')
    sys.stdout.flush()

def execute_command(cmd, show=True):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    out, err = out.decode(), err.decode()
    if show:
        if out != '':
            print(out)
        if err != '':
            print(err)
    return out, err, p

def execute_table_command(command, columns, data, delimiter, show_command):
    with tempfile.NamedTemporaryFile(mode='w') as fp:
        path = fp.name
        cmd = command.format(path=path)
        save_table_data(path, columns, data, show_save_message=False)
        if show_command:
            print(f'[Command] {cmd}')
        execute_command(cmd)

def make_grep_command(pattern):
    if not pattern:
        return
    pat_split = [p.strip() for p in pattern.split(',')]
    try:
        pat0 = f'grep -ve {pat_split[0][1:]}' if pat_split[0][0] == '-' else f'grep -e {pat_split[0]}'
        pat1 = ' '.join([f'| grep -ve {p[1:]}' if p[0] == '-' else f'| grep -e {p}' for p in pat_split[1:]])
        pat = f'{pat0} {pat1}'.strip()
    except Exception:
        print('[Error] Something wrong with GrepRun')
        return ''
    return pat
