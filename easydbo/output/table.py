class TableOutput:
    @staticmethod
    def table(data_all):
        for idx_data in range(len(data_all)):
            data_i = data_all[idx_data]
            sheet = data_i.name
            columns = data_i.columns
            for del_or_ins in ['insert', 'delete']:
                data_d_r_i = data_i.insert if del_or_ins == 'insert' else data_i.delete
                if data_d_r_i:
                    data_2d = [columns] + data_d_r_i
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
                    out = f'{del_or_ins[0].upper() + del_or_ins[1:]} from {sheet} table\n'
                    for i, (data_1d, space_1d) in enumerate(zip(data_2d, space_2d)):
                        row, sep = ('+-', '-+-') if i in idx_line else ('| ', ' | ')
                        for data_d0, space_d0 in zip(data_1d, space_1d):
                            row += f'{" " * space_d0}{data_d0}{sep}'
                        row = row[:-1]
                        out += row + "\n"
                    print(out)
