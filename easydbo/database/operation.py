import getpass
from mysql import connector
from easydbo.output.log import Log

class DatabaseOperation:
    def __init__(self, config):
        self.password = None
        self.config = config
        self.is_connect = False

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

    def get_key_val_cond(self, keys, vlaues):
        return ' OR '.join([
            '(' + ' AND '.join([f'{k}="{v}"' for k, v in zip(keys, val)]) + ')'
            for val in vlaues])

    def get_current_columns(self):
        return list(self.cursor.column_names)

    def get_current_statement(self):
        return self.cursor.statement

    # Select --->

    def _select(self, cmd, ret_flat):
        self.cursor.execute(cmd)  # QUESTION: should use multi=True?
        rows = self.cursor.fetchall()
        return [str(d) for r in rows for d in r] if ret_flat else [[str(d) for d in r] for r in rows]

    def select(self, table, columns, where='', ret_flat=False):
        columns = ','.join(columns)
        where = f'WHERE {where}' if where else ''
        cmd = f'SELECT {columns} FROM {table} {where};'
        return self._select(cmd, ret_flat)

    def select_by_cmd(self, cmd, ret_flat=False):
        return self._select(cmd, ret_flat)

    # <---

    def insert(self, table, columns, data):
        '''
        table  : str    : table name
        columns: 1D list: column names
        data   : 1D list: data to input
        '''
        col_str = ','.join(columns)
        cmd = f'INSERT INTO {table}({col_str}) VALUES ({("%s, "*len(data[0]))[:-2]});'
        self.cursor.executemany(cmd, data)

    def delete_by_pk(self, table, pk, pvs):
        '''
        table: str    : table name
        pk   : str    : primary key
        pvs  : 1D list: primary values
        '''
        pvs_str = f'({pvs[0]})' if len(pvs) == 1 else str(tuple(pvs))
        where = f'{pk} in {pvs_str}'
        self.delete(table, where)

    def delete(self, table, where=''):
        cmd = f'DELETE FROM {table} WHERE {where};'
        self.cursor.execute(cmd)

    def update(self, table, cols_vals, pn, pv):
        '''
        table    : str : table name
        cols_vals: dict: pair of columns and values
        pn       : str : primary names
        pv       : str : primary values
        '''
        set_ = ', '.join([f'{c}="{v}"' for c, v in cols_vals.items()])
        where = f'{pn}={pv}'
        cmd = f'UPDATE {table} SET {set_} WHERE {where};'
        self.cursor.execute(cmd)

    def commit(self):
        if self.is_connect:
            self.conn.commit()

    def close(self):
        if self.is_connect:
            self.conn.close()

# create table
#results = self.cursor.execute(operations, multi=True)
#for r in results:
#    print(r)
