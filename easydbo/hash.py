import hashlib

class HashCreator:
    def __init__(self):
        self.separator = '|'

    def create(self, data2d):
        data1d = [self.separator.join(li) for li in data2d]
        hash1d = [hashlib.sha256(bytes(data, encoding='utf8')).hexdigest() for data in data1d]
        if len(hash1d) != len(set(hash1d)):
            print('[Error] Hash is not unique')
            print(f'len(hash1): {len(hash1d)}, len(set(hash1d)): {len(set(hash1d))}')
            print(f'data\n{data1d}')
            print(f'hash\n{hash1d}')
            exit(1)
        return hash1d

class HashDiff:
    def __init__(self, hash1, hash2):
        self.hash1 = hash1
        self.hash2 = hash2

    def get_noncom_idx(self):
        r_idx1 = []
        hash2_idx = {h: i for i, h in enumerate(self.hash2)}
        for idx1, hash1 in enumerate(self.hash1):
            try:
                hash2_idx.pop(hash1)
            except KeyError:
                r_idx1.append(idx1)
        return r_idx1, list(hash2_idx.values())

if __name__ == '__main__':
    hash_creator = HashCreator()
    hash1 = hash_creator.create([['a', 'b'], ['b', 'c'], ['c', 'd']])
    hash2 = hash_creator.create([['b', 'c'], ['c', 'd'], ['e', 'f']])
    print(hash1)
    print(hash2)
    hash_diff = HashDiff(hash1, hash2)
    idx1, idx2 = hash_diff.get_noncom_idx()
    print(idx1)
    print(idx2)
