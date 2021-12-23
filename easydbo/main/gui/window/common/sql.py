from ..query import QueryResultWindow

def create_sql_result(query, util, subwinmgr, location):
    dbop = util.dbop
    ret = dbop.execute(query, ignore_error=True)
    if ret.is_error:
        return
    header = dbop.get_current_columns()
    data = dbop.fetchall()
    # Print data on new window
    subwinmgr.create_window(QueryResultWindow, util, query, header, data, location)
