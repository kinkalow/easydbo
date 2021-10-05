import getpass
from mysql import connector
from easydbo.output.log import Log

class DatabaseOperation:
    def __init__(self, config):
        self.password = None
        self.config = config

        self._init()

    def _init(self):
        cfg = {k: v for k, v in self.config.items() if v}
        conn = connector.connect(**cfg)
        if not conn.is_connected():
            Log.error('Connection to MySQL server failed')
        self.conn = conn
        self.cursor = conn.cursor(buffered=True)

    def authenticate(self):
        self.password = ''
        if self.password is None:
            self.password = getpass.getpass('Enter database possword: ')

    #def _select(self, cmd):
    #    self.cursor.execute(cmd)  # QUESTION: should use multi=True?
    #    rows = self.cursor.fetchall()
    #    data = [[str(d) for d in r] for r in rows]
    #    return data

    def select(self, table, columns, where=''):
        columns = ','.join(columns)
        where = 'WHERE {where}' if where else ''
        cmd = f'SELECT {columns} FROM {table} {where};'
        self.cursor.execute(cmd)  # QUESTION: should use multi=True?
        rows = self.cursor.fetchall()
        data = [[str(d) for d in r] for r in rows]
        return data

    def insert(self, table, columns, data):
        '''
        table  : str    : table name
        columns: 1D list: column names
        data   : 1D list: data to input
        '''
        col_str = ','.join(columns)
        cmd = f'INSERT INTO {table}({col_str}) VALUES ({("%s, "*len(data[0]))[:-2]});'
        self.cursor.executemany(cmd, data)
        #self.conn.commit()

    def delete_by_pk(self, table, pk, pvs):
        '''
        table: str    : table name
        pk   : str    : primary key
        pvs  : 1D list: primary values
        '''
        pvs_str = f'({pvs[0]})' if len(pvs) else str(tuple(pvs))
        where = f'{pk} in {pvs_str}'
        self.delete(table, where)

    def delete(self, table, where=''):
        cmd = f'DELETE FROM {table} WHERE {where};'
        self.cursor.execute(cmd)
        #self.conn.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

# create table
#results = self.cursor.execute(operations, multi=True)
#for r in results:
#    print(r)
