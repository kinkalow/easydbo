from easydbo.output.log import Log

def execute_query(dbop, sql):
    # Access database
    dbop.authenticate()
    rows = dbop.select_by_cmd(sql)  # Perform this method first
    columns = dbop.get_current_columns()
    title = dbop.get_current_statement()
    if not rows:
        Log.info(title)
    return title, columns, rows

def main(arguments, configs, tableop, dbop):
    sql = arguments.sql
    return execute_query(dbop, sql)
