from easydbo.init.alias import AliasLoader

def main(arguments, configs, tableop, dbop):
    alias_loader = AliasLoader()
    aliases = alias_loader.get()
    names = [a.name for a in aliases]
    querys = [a.query for a in aliases]

    title = ''
    columns = ['Alias', 'Query']
    rows = list(zip(names, querys))
    return title, columns, rows
