import unittest
from simulate_cache import LRUCache, LFUCache, PredictiveCache, generate_sequence, run_simulation

class TestCachesExtended(unittest.TestCase):
    def test_lru_eviction_order(self):
        c = LRUCache(3)
        c.access(1)
        c.access(2)
        c.access(3)
        c.access(4)
        # 1 should be evicted
        self.assertNotIn(1, c.od)

    def test_lfu_eviction_by_frequency(self):
        c = LFUCache(2)
        # access 1 multiple times
        c.access(1)
        c.access(1)
        c.access(2)
        c.access(3)
        # 1 should remain due to higher freq
        self.assertIn(1, c.store)

    def test_predictive_prefetch_effect(self):
        c = PredictiveCache(3)
        seq = [1,2,1,3,1,2,4,5,1,2]
        for i,k in enumerate(seq,1):
            c.access(k, i)
        # prefetch_count should be non-negative
        self.assertGreaterEqual(c.prefetch_count, 0)

    def test_generate_sequence_distribution(self):
        seq = generate_sequence(500, 1000)
        # expect variety of keys
        self.assertGreater(len(set(seq)), 50)

    def test_run_simulation_small(self):
        # ensure function runs and returns tuples
        lru, lfu, pred = run_simulation(num_keys=500, seq_len=1000, cache_capacity=100, quiet=True)
        self.assertEqual(len(lru), 4)

if __name__ == '__main__':
    unittest.main()
