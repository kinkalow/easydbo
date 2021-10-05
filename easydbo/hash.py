import hashlib
from easydbo.output.log import Log

class HashCreator:
    def __init__(self):
        self.separator = '|'

    def create(self, data2d):
        data1d = [self.separator.join(li) for li in data2d]
        hash1d = [hashlib.sha256(bytes(data, encoding='utf8')).hexdigest() for data in data1d]
        if len(hash1d) != len(set(hash1d)):
            Log.error(['Hash is not unique',
                       f'len(hash1): {len(hash1d)}',
                       f'len(set(hash1d)): {len(set(hash1d))}',
                       f'data: {data1d}',
                       f'hash: {hash1d}'])
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
