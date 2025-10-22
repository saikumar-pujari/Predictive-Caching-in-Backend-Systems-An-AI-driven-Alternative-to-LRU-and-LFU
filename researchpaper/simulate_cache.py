"""
Pure-Python cache simulator that avoids external dependencies.
Generates `sim_results.svg` in the same folder and prints summary metrics.
"""
import random
import time
import math
from collections import OrderedDict, defaultdict, deque

DEFAULT_NUM_KEYS = 10000
DEFAULT_SEQ_LEN = 200000
DEFAULT_CACHE_CAPACITY = 2000
BURST_COUNT = 100
BURST_SIZE = 30
PREFETCH_THRESHOLD = 0.5
PREFETCH_CAP = 50  # max prefetches per batch
BATCH_PREDICT_EVERY = 1000

random.seed(0)

# Generate a Zipf-like popularity via weights and random.choices
def generate_sequence(num_keys, seq_len, s=0.8):
    weights = [1.0 / ((i + 1) ** s) for i in range(num_keys)]
    total = sum(weights)
    probs = [w / total for w in weights]
    population = list(range(num_keys))
    seq = random.choices(population, weights=probs, k=seq_len)
    return seq

seq = generate_sequence(DEFAULT_NUM_KEYS, DEFAULT_SEQ_LEN)

# Inject bursts for temporal locality
for _ in range(BURST_COUNT):
    pos = random.randint(0, DEFAULT_SEQ_LEN - BURST_SIZE - 1)
    key = random.randint(0, DEFAULT_NUM_KEYS - 1)
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


# Simple LFU cache (naive)
class LFUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = {}
        self.counts = defaultdict(int)
        self.order = {}
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
        self.predicted = {}
        self.history = deque(maxlen=5000)
        self.prefetch_count = 0

    def access(self, key, step):
        self.history.append(key)
        if key in self.store:
            self.hits += 1
            self.store.move_to_end(key)
        else:
            self.misses += 1
            if len(self.store) >= self.capacity:
                self.store.popitem(last=False)
            self.store[key] = True
        if step % BATCH_PREDICT_EVERY == 0:
            self.batch_update_and_prefetch()

    def batch_update_and_prefetch(self):
        W = 200
        recent = list(self.history)[-W:]
        counts = defaultdict(int)
        for k in recent:
            counts[k] += 1
        if counts:
            maxc = max(counts.values())
            for k, v in counts.items():
                self.predicted[k] = v / maxc
        candidates = sorted(self.predicted.items(), key=lambda kv: -kv[1])
        prefetched = 0
        for k, score in candidates:
            if prefetched >= PREFETCH_CAP:
                break
            if score > PREFETCH_THRESHOLD and k not in self.store:
                if len(self.store) >= self.capacity:
                    self.store.popitem(last=False)
                self.store[k] = True
                prefetched += 1
        self.prefetch_count += prefetched


def compute_metrics(cache):
    hits = cache.hits
    misses = cache.misses
    total = hits + misses
    hit_rate = hits / total if total > 0 else 0
    avg_latency = hit_rate * 5.0 + (1 - hit_rate) * 80.0
    return hit_rate, avg_latency, hits, misses


def run_simulation(num_keys=DEFAULT_NUM_KEYS, seq_len=DEFAULT_SEQ_LEN, cache_capacity=DEFAULT_CACHE_CAPACITY, quiet=False):
    # regenerate sequence per run with provided parameters
    seq = generate_sequence(num_keys, seq_len)
    for _ in range(BURST_COUNT):
        pos = random.randint(0, seq_len - BURST_SIZE - 1)
        key = random.randint(0, num_keys - 1)
        for i in range(BURST_SIZE):
            seq[pos + i] = key

    lru = LRUCache(cache_capacity)
    lfu = LFUCache(cache_capacity)
    pred = PredictiveCache(cache_capacity)

    start = time.time()
    for i, k in enumerate(seq, 1):
        lru.access(k)
        lfu.access(k)
        pred.access(k, i)
    end = time.time()

    lru_metrics = compute_metrics(lru)
    lfu_metrics = compute_metrics(lfu)
    pred_metrics = compute_metrics(pred)

    if not quiet:
        print("Simulation finished in", round(end - start, 2), "seconds")
        print("LRU: hit_rate={:.4f}, avg_latency={:.2f} ms".format(lru_metrics[0], lru_metrics[1]))
        print("LFU: hit_rate={:.4f}, avg_latency={:.2f} ms".format(lfu_metrics[0], lfu_metrics[1]))
        print("Predictive: hit_rate={:.4f}, avg_latency={:.2f} ms, prefetches={}".format(pred_metrics[0], pred_metrics[1], pred.prefetch_count))

    # Create a simple SVG chart (no external libs)
    policies = ['LRU', 'LFU', 'Predictive']
    hit_rates = [lru_metrics[0], lfu_metrics[0], pred_metrics[0]]
    latencies = [lru_metrics[1], lfu_metrics[1], pred_metrics[1]]

    svg_w = 800
    svg_h = 400
    margin = 60
    bar_w = 80
    gap = 40

    max_latency = max(latencies) * 1.2 if latencies else 1.0

    svg_lines = [f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">']
    svg_lines.append('<style>text { font-family: Arial; font-size: 12px; }</style>')
    # Draw hit rate bars (left)
    for i, rate in enumerate(hit_rates):
        x = margin + i * (bar_w + gap)
        h = (svg_h - 2 * margin) * rate
        y = svg_h - margin - h
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#1f77b4" />')
        svg_lines.append(f'<text x="{x + bar_w/2}" y="{svg_h - margin + 18}" text-anchor="middle">{policies[i]}</text>')
        svg_lines.append(f'<text x="{x + bar_w/2}" y="{y - 6}" text-anchor="middle" fill="#000">{rate:.2f}</text>')

    # Draw latency bars (right, smaller, overlayed with opacity)
    for i, lat in enumerate(latencies):
        x = margin + i * (bar_w + gap) + bar_w/2
        h = (svg_h - 2 * margin) * (lat / max_latency)
        y = svg_h - margin - h
        svg_lines.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#ff7f0e" opacity="0.8" />')
        svg_lines.append(f'<text x="{x + bar_w/2}" y="{y - 6}" text-anchor="middle" fill="#000">{lat:.1f} ms</text>')

    svg_lines.append(f'<text x="{svg_w/2}" y="20" text-anchor="middle" font-size="16">Cache policy comparison — hit rate (blue) and avg latency (orange)</text>')
    svg_lines.append('</svg>')

    with open('sim_results.svg', 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_lines))
    if not quiet:
        print('Saved sim_results.svg')

    return lru_metrics, lfu_metrics, pred_metrics


if __name__ == '__main__':
    run_simulation()
