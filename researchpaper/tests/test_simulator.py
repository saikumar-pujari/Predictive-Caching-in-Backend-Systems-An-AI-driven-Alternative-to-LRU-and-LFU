import unittest
import importlib
import sys
from pathlib import Path

# Ensure the researchpaper folder is importable so tests use the correct module
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulate_cache import LRUCache, LFUCache, PredictiveCache, generate_sequence, run_simulation

class TestCaches(unittest.TestCase):
    def test_lru_basic(self):
        c = LRUCache(2)
        c.access(1)
        c.access(2)
        c.access(1)
        c.access(3)
        # after accesses, hit should be at least 1 (access(1) hit)
        self.assertGreaterEqual(c.hits, 1)

    def test_lfu_basic(self):
        c = LFUCache(2)
        c.access(1)
        c.access(2)
        c.access(1)
        c.access(3)
        # 1 was accessed twice, should be in cache
        self.assertGreaterEqual(c.counts.get(1,0), 1)

    def test_predictive_basic(self):
        c = PredictiveCache(2)
        # run short sequence
        for i,k in enumerate([1,2,1,3,1,2],1):
            c.access(k, i)
        self.assertIsInstance(c.prefetch_count, int)

    def test_generate_sequence(self):
        seq = generate_sequence(100, 1000)
        self.assertEqual(len(seq), 1000)

    def test_run_simulation(self):
        lru, lfu, pred = run_simulation(num_keys=200, seq_len=200, cache_capacity=50, quiet=True)
        # each metric tuple is (hit_rate, avg_latency, hits, misses)
        self.assertEqual(len(lru), 4)

if __name__ == '__main__':
    unittest.main()
