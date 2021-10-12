import argparse
import os
from easydbo import __version__


class Base:
    def get(self):
        return self._args


class ArgumentLoader(Base):
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydboexcel'
        parser = argparse.ArgumentParser(prog=prog)
        #parser.add_argument('operation', type=str, choices=['bam', 'excel', 'vcf', 'search'], help="choose 'bam', 'excel', 'vcf', or 'search'")
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
