import argparse
import os
from easydbo import __version__
#from easydbo.output.print_ import SimplePrint as SP


class Base:
    def get(self):
        return self._args


class ArgumentExcelLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydboexcel'
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('excel_path', type=str, help='excel path')
        parser.add_argument('--reset', type=bool, help='reset the elements in the id column to continuous values')
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')

        self._args = parser.parse_args()
        self._convert(self._args)

    def _convert(self, args):
        args.excel_path = os.path.abspath(args.excel_path)


class ArgumentInsertLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydboinsert'
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('table', type=str, help='table name')
        parser.add_argument('fields', type=str, nargs='+', help='field values')
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')
        self._args = parser.parse_args()
        self._convert(self._args)

    def _convert(self, args):
        args.fields = [[f if f else None for f in args.fields]]


class ArgumentDeleteLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydbodelete'
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('table', type=str, help='table name')
        parser.add_argument('pks', type=str, nargs='+', help='primary key values')
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')
        self._args = parser.parse_args()


class ArgumentUpdateLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydboupdate'
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('table', type=str, help='table name')
        parser.add_argument('pk', type=str, help='primary key values')
        parser.add_argument('pairs', type=str, nargs='+', help='key-value pair in fields')
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')
        self._args = parser.parse_args()
        self._convert(self._args)

    def _convert(self, args):
        d = {}
        for p in args.pairs:
            k, v = p.split(':')
            d[k] = v
        args.pairs = d

class ArgumentSelectLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        class MatchColumns(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                setattr(namespace, self.dest, values.strip()) if values else \
                setattr(namespace, self.dest, '*')

        prog = 'easydboselect'
        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')
        subparsers = parser.add_subparsers()

        alias_parser = subparsers.add_parser('alias', help='alias for SELECT statement in SQL')
        alias_parser.add_argument('name', type=str, help='alias name')

        match_parser = subparsers.add_parser('match', help='simple selection query')
        match_parser.add_argument('columns', nargs='?', action=MatchColumns, type=str, help='SELECT clause in SQL')
        match_parser.add_argument('conditions', nargs='?', type=str, default='', help='WHERE clause in SQL')
        match_parser.add_argument('tables', nargs='?', type=str, default='', help='FROM clause in SQL')

        subparsers.add_parser('show_alias', help="show alias name and it's query")

        sql_parser = subparsers.add_parser('sql', help='selection query')
        sql_parser.add_argument('sql', type=str, help='SELECT statement in SQL')

        import sys
        argvs = sys.argv[1:]
        self._args = parser.parse_args(argvs)
        self._args.main = argvs[0]
