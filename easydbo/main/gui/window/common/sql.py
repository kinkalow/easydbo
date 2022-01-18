from ..query import QueryResultWindow

def create_query_result_window(query, pack, subwin, location):
    dbop = pack.dbop
    ret = dbop.execute(query, ignore_error=True)
    if ret.is_error:
        return
    header = dbop.get_current_columns()
    data = dbop.fetchall()
    # Print data on new window
    subwin.create_multiples(QueryResultWindow, pack, query, header, data, location)
