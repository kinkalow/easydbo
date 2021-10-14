from easydbo.init.alias import AliasLoader

def main(arguments, configs, tableop, dbop):
    alias_loader = AliasLoader()
    aliases = alias_loader.get()
    names = [a.name for a in aliases]
    sqls = [a.sql for a in aliases]

    title = ''
    columns = ['Alias', 'SQL']
    rows = list(zip(names, sqls))
    return title, columns, rows
