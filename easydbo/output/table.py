from easydbo.output.log import Log

class TableOutput:
    @staticmethod
    def table(data_all):
        for idx_data in range(len(data_all)):
            data_i = data_all[idx_data]
            title = data_i['title'] if 'title' in data_i else ''
            name = data_i['name'] if 'name' in data_i else ''
            columns = data_i['columns']
            for op in ['insert', 'delete', 'update', 'select']:
                if op not in data_i:
                    continue
                data_op = data_i[op]
                if data_op:
                    data_2d = [columns] + data_op
                    len_2d = [[len(data_d0) for data_d0 in data_1d] for data_1d in data_2d]
                    maxlen_1d = [0] * len(len_2d[0])
                    for len_1d in len_2d:
                        for i, len_d0 in enumerate(len_1d):
                            if len_d0 > maxlen_1d[i]:
                                maxlen_1d[i] = len_d0
                    space_2d = [[maxlen_d0 - len_d0 for len_d0, maxlen_d0 in
                                 zip(len_1d, maxlen_1d)] for len_1d in len_2d]
                    # Add lines like '+---+---+'
                    idx_line = [0, 2, len(data_2d) + 2]
                    line = ['-' * maxlen_d0 for maxlen_d0 in maxlen_1d]
                    for i in idx_line:
                        data_2d.insert(i, line)
                        space_2d.insert(i, [0] * len(len_2d[0]))
                    # Print
                    out = f'{title}\n' if title \
                    else f'{op[0].upper() + op[1:]} from {name} table\n' if name \
                    else ''
                    for i, (data_1d, space_1d) in enumerate(zip(data_2d, space_2d)):
                        row, sep = ('+-', '-+-') if i in idx_line else ('| ', ' | ')
                        for data_d0, space_d0 in zip(data_1d, space_1d):
                            row += f'{" " * space_d0}{data_d0}{sep}'
                        row = row[:-1]
                        out += row + "\n"
                    Log.info(out)

    @staticmethod
    def fulltable(data_all, dbop):
        fulltbls = []
        for idx, di in enumerate(data_all):
            t = {}
            t['name'] = di.name
            if di.pkidx == -1:
                t['columns'] = [di.pk] + di.columns
                t['delete'] = [[di.delete_by_pk[i]] + d for i, d in enumerate(di.delete)]
                where = dbop.get_key_val_cond(di.columns, di.insert)
                pks = dbop.select(di.name, [di.pk], where=where)
                t['insert'] = [pk + ins for pk, ins in zip(pks, di.insert)]
                #t['update'] = [[di.update_by_pk[i]] + d for i, d in enumerate(di.update)]
                where = dbop.get_key_val_cond(di.columns, di.update)
                pks = dbop.select(di.name, [di.pk], where=where)
                t['update'] = [pk + ins for pk, ins in zip(pks, di.update)]
            else:
                t['columns'] = di.columns
                t['insert'] = di.insert
                t['delete'] = di.delete
                t['update'] = di.update
            fulltbls.append(t)
        TableOutput.table(fulltbls)
