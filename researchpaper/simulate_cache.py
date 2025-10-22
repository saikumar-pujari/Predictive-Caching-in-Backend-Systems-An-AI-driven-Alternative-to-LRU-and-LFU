"""
Simple cache simulator for LRU, LFU, and a basic predictive cache.
Saves a comparison PNG as sim_results.png in the same folder.
Requires: numpy, matplotlib

This script was tested in a personal IDE while developing the examples.
"""
import random
import time
from collections import OrderedDict, defaultdict, deque
import numpy as np
import matplotlib.pyplot as plt

NUM_KEYS = 10000
SEQ_LEN = 200000
CACHE_CAPACITY = 2000
BURST_COUNT = 100
BURST_SIZE = 30
PREFETCH_THRESHOLD = 0.5
PREFETCH_CAP = 50  # max prefetches per 1000 events
BATCH_PREDICT_EVERY = 1000

# Generate a base popularity using a Zipf-like distribution
np.random.seed(0)
# numpy.zipf needs a parameter >1; use 1.3 and map into range
raw = np.random.zipf(1.3, size=SEQ_LEN)
seq = ((raw - 1) % NUM_KEYS).astype(int).tolist()

# Inject bursts: pick random positions and repeat a favored key several times
for _ in range(BURST_COUNT):
    pos = random.randint(0, SEQ_LEN - BURST_SIZE - 1)
    key = random.randint(0, NUM_KEYS - 1)
    for i in range(BURST_SIZE):
        seq[pos + i] = key

# Simple LRU cache
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.od = OrderedDict()
        self.hits = 0
        self.misses = 0
    def access(self, key):
        if key in self.od:
            self.hits += 1
            self.od.move_to_end(key)
        else:
            self.misses += 1
            if len(self.od) >= self.capacity:
                self.od.popitem(last=False)
            self.od[key] = True

# Simple LFU cache (naive eviction by scanning counts)
class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}
        self.counts = defaultdict(int)
        self.order = {}  # insert time for tie-break
        self.time = 0
        self.hits = 0
        self.misses = 0
    def access(self, key):
        self.time += 1
        if key in self.store:
            self.hits += 1
            self.counts[key] += 1
        else:
            self.misses += 1
            if len(self.store) >= self.capacity:
                # find least-freq key (naive)
                victim = min(self.store.keys(), key=lambda k: (self.counts[k], self.order[k]))
                del self.store[victim]
                del self.counts[victim]
                del self.order[victim]
            self.store[key] = True
            self.counts[key] = 1
            self.order[key] = self.time

# Predictive cache: uses recent-window frequency as "model" score and prefetches
class PredictiveCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.predicted = {}  # predicted_score per key
        self.history = deque(maxlen=5000)  # recent access history
        self.prefetch_count = 0
    def access(self, key, step):
        # update history
        self.history.append(key)
        score = self.predicted.get(key, 0.0)
        if key in self.store:
            self.hits += 1
            self.store.move_to_end(key)
        else:
            self.misses += 1
            if len(self.store) >= self.capacity:
                self.store.popitem(last=False)
            self.store[key] = True
        # periodic batch update and controlled prefetch
        if step % BATCH_PREDICT_EVERY == 0:
            self.batch_update_and_prefetch(step)
    def batch_update_and_prefetch(self, step):
        # simple prediction: keys seen in last W are likely to be requested
        W = 200
        recent = list(self.history)[-W:]
        counts = defaultdict(int)
        for k in recent:
            counts[k] += 1
        # normalize to [0,1]
        if counts:
            maxc = max(counts.values())
            for k, v in counts.items():
                self.predicted[k] = v / maxc
        # prefetch top candidates up to PREFETCH_CAP per batch
        candidates = sorted(self.predicted.items(), key=lambda kv: -kv[1])
        prefetched = 0
        for k, score in candidates:
            if prefetched >= PREFETCH_CAP:
                break
            if score > PREFETCH_THRESHOLD and k not in self.store:
                # prefetch into cache with short TTL simulated by insertion
                if len(self.store) >= self.capacity:
                    self.store.popitem(last=False)
                self.store[k] = True
                prefetched += 1
        self.prefetch_count += prefetched

# Run the simulation
lru = LRUCache(CACHE_CAPACITY)
lfu = LFUCache(CACHE_CAPACITY)
pred = PredictiveCache(CACHE_CAPACITY)

start = time.time()
for i, k in enumerate(seq, 1):
    lru.access(k)
    lfu.access(k)
    pred.access(k, i)
end = time.time()

# Metrics
def compute_metrics(cache):
    hits = cache.hits
    misses = cache.misses
    total = hits + misses
    hit_rate = hits / total if total > 0 else 0
    avg_latency = hit_rate * 5.0 + (1 - hit_rate) * 80.0
    return hit_rate, avg_latency, hits, misses

lru_metrics = compute_metrics(lru)
lfu_metrics = compute_metrics(lfu)
pred_metrics = compute_metrics(pred)

print("Simulation finished in", round(end - start, 2), "seconds")
print("LRU: hit_rate={:.4f}, avg_latency={:.2f} ms".format(lru_metrics[0], lru_metrics[1]))
print("LFU: hit_rate={:.4f}, avg_latency={:.2f} ms".format(lfu_metrics[0], lfu_metrics[1]))
print("Predictive: hit_rate={:.4f}, avg_latency={:.2f} ms, prefetches={}".format(pred_metrics[0], pred_metrics[1], pred.prefetch_count))

# Save a simple bar chart
policies = ['LRU', 'LFU', 'Predictive']
hit_rates = [lru_metrics[0], lfu_metrics[0], pred_metrics[0]]
latencies = [lru_metrics[1], lfu_metrics[1], pred_metrics[1]]

fig, ax1 = plt.subplots(figsize=(8,5))
ax2 = ax1.twinx()

x = np.arange(len(policies))
ax1.bar(x - 0.2, hit_rates, width=0.4, label='Hit Rate', color='tab:blue')
ax2.bar(x + 0.2, latencies, width=0.4, label='Avg Latency (ms)', color='tab:orange')

ax1.set_xticks(x)
ax1.set_xticklabels(policies)
ax1.set_ylabel('Hit rate')
ax2.set_ylabel('Avg latency (ms)')
ax1.set_ylim(0,1)

for i, v in enumerate(hit_rates):
    ax1.text(i - 0.3, v + 0.02, f"{v:.2f}")
for i, v in enumerate(latencies):
    ax2.text(i + 0.1, v + 1, f"{v:.1f}")

plt.title('Cache policy comparison — hit rate and avg latency')
fig.tight_layout()
plt.savefig('sim_results.png', dpi=150)
print('Saved sim_results.png')
