import re
import getpass
from mysql import connector
from easydbo.output.log import Log

class DatabaseOperation:
    def __init__(self, config):
        self.password = None
        self.config = config
        self.is_connect = False
        self.on_query_error = None
        self._is_execution_error = False
        #
        self._init()

    def _init(self):
        cfg = {k: v for k, v in self.config.items() if v}
        conn = connector.connect(**cfg)
        if not conn.is_connected():
            Log.error('Connection to MySQL server failed')
        self.conn = conn
        self.cursor = conn.cursor(buffered=True)
        self.is_connect = True

    def authenticate(self):
        self.password = ''
        if self.password is None:
            self.password = getpass.getpass('Enter database possword: ')

    # Get --->

    def get_autoincrement(self, table, column):
        query = f'''
SELECT Min(_EASYDBO_TABLE.{column})+1 AS min_num FROM (SELECT {column} FROM {table} UNION ALL SELECT 0 AS {column}) _EASYDBO_TABLE LEFT JOIN {table} ON _EASYDBO_TABLE.{column} + 1 = {table}.{column} WHERE {table}.{column} IS NULL;
'''.strip()
        self.execute(query)
        return self.fetchall()[0][0]

    def get_key_val_cond(self, keys, vlaues):
        return ' OR '.join([
            '(' + ' AND '.join([f'{k}="{v}"' for k, v in zip(keys, val)]) + ')'
            for val in vlaues])

    def get_current_columns(self):
        return list(self.cursor.column_names)

    def get_current_query(self):
        return self.cursor.statement

    # <---
    # Select --->

    def _select(self, query, ret_flat, **kwargs):
        self.execute(query, **kwargs)
        rows = self.fetchall()
        return [str(d) for r in rows for d in r] if ret_flat else [[str(d) for d in r] for r in rows]

    def select(self, table, columns, where='', ret_flat=False, **kwargs):
        columns = ','.join(columns)
        where = f'WHERE {where}' if where else ''
        query = f'SELECT {columns} FROM {table} {where};'
        return self._select(query, ret_flat, **kwargs)

    def select_by_cmd(self, query, ret_flat=False, **kwargs):
        return self._select(query, ret_flat, **kwargs)

    # <---
    # Insert --->

    def insert(self, table, columns, data, do_convert=False, **kwargs):
        '''
        table  : str                    : Table name
        columns: List(str)              : Column names
        data   : List(List(str or None)): Data to input
        '''
        col_str = ','.join(columns)
        query = f'INSERT INTO {table}({col_str}) VALUES ({("%s, "*len(data[0]))[:-2]});'
        if do_convert:
            data_conv = [None if not d0 else d0 if isinstance(d0, str) else str(d0) for d1 in data for d0 in d1]
        else:
            data_conv = data
        return self.executemany(query, data_conv, **kwargs)

    # <---
    # Delete --->

    def delete_by_pk(self, table, pk, pvs, **kwargs):
        '''
        table: str    : table name
        pk   : str    : table column name for primary key
        pvs  : 1D list: primary values
        '''
        targets = ', '.join([pv if isinstance(pv, str) and re.match(r'"|\'', pv) else f'"{pv}"' for pv in pvs])
        where = f'{pk} in ({targets})'
        return self.delete(table, where, **kwargs)

    def delete(self, table, where='', **kwargs):
        query = f'DELETE FROM {table} WHERE {where};'
        return self.execute(query, **kwargs)

    # <---
    # Update --->

    def update(self, table, cols_vals, pn, pv, **kwargs):
        '''
        table    : str                   : table name
        cols_vals: Dict{str: str or None}: pair of columns and values
        pn       : str                   : primary name
        pv       : str                   : primary value
        '''
        set_ = ', '.join([f'{c}="{v}"' if v else f'{c}=NULL' for c, v in cols_vals.items()])
        where = f'{pn}={pv}'
        query = f'UPDATE {table} SET {set_} WHERE {where};'
        return self.execute(query, **kwargs)

    # <---
    # Execute --->

    def _handle_execution_error(self, error, query, ignore_error=False, print_error=True):
        errors = [str(error), f'QUERRY: {query}']
        if ignore_error:
            if print_error:
                Log.error(errors, ignore_exit=True)
            return
        elif self.on_query_error:
            self.on_query_error()
        self.close()
        if print_error:
            Log.error(errors, traceback=True, ignore_exit=False)

    def execute(self, query, data=[], multi=False, **kwargs):
        class Info:
            is_error = False
            error_content = ''
        info = Info()
        try:
            if data:
                self.cursor.executemany(query, data)
            else:
                self.cursor.execute(query, multi)
        except Exception as e:
            info.is_error = True
            info.error_content = str(e)
            self._handle_execution_error(e, query, **kwargs)
        return info

    def executemany(self, query, data, **kwargs):
        return self.execute(query, data=data, **kwargs)

    def set_query_error(self, f=None):
        self.on_query_error = f

    # <---

    def commit(self):
        if self.is_connect:
            self.conn.commit()

    def fetchall(self):
        return self.cursor.fetchall()

    def rollback(self):
        if self.is_connect:
            self.conn.rollback()

    def close(self):
        if self.is_connect:
            self.conn.close()
