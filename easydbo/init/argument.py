import argparse
import os
from easydbo import __version__


class ArgumentGetter:
    def __init__(self):
        self._parse()

    def _parse(self):
        prog = 'easydbo'

        parser = argparse.ArgumentParser(prog=prog)
        parser.add_argument('operation', type=str, choices=['bam', 'excel', 'vcf', 'search'], help="choose 'bam', 'excel', 'vcf', or 'search'")
        parser.add_argument('excel_path', type=str, help='excel path')
        parser.add_argument('--reset', type=bool, help='reset the elements in the id column to continuous values')
        parser.add_argument('--version', action='version', version=f'{prog}: {__version__}')

        self._args = parser.parse_args()
        self._convert(self._args)

    def _convert(self, args):
        args.excel_path = os.path.abspath(args.excel_path)

    def get(self):
        return self._args
