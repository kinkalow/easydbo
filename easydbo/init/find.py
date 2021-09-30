import os

class Finder:
    def find(self, file):
        path1 = f'{os.path.abspath(".")}/{file}'
        path2 = f'{os.environ["EASYDBOPATH"]}/{file}' if 'EASYDBOPATH' in os.environ else ''
        path3 = os.path.expanduser(f'~/.cache/easydbo/{file}')
        if os.path.exists(path1):
            return path1
        elif os.path.exists(path2):
            return path2
        elif os.path.exists(path3):
            return path3
        else:
            print(f'[Error] does not exist file: {file}')
            exit(1)
