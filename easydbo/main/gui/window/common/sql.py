from ..query import QueryResultWindow

def create_sql_result(query, pack, subwinmgr, location):
    dbop = pack.dbop
    ret = dbop.execute(query, ignore_error=True)
    if ret.is_error:
        return
    header = dbop.get_current_columns()
    data = dbop.fetchall()
    # Print data on new window
    subwinmgr.create_window(QueryResultWindow, pack, query, header, data, location)
