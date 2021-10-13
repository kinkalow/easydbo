import unittest
from easydbo.util.hash import HashCreator, HashDiff

class TestHashDiff(unittest.TestCase):
    def test_hash_diff(self):
        hash_creator = HashCreator()
        hash1 = hash_creator.create([['a', 'b'], ['b', 'c']])
        hash2 = hash_creator.create([['b', 'c'], ['c', 'd']])
        hash_diff = HashDiff(hash1, hash2)
        idx1, idx2 = hash_diff.get_noncom_idx()
        self.assertEqual(idx1, [0])
        self.assertEqual(idx2, [1])
