"""
Run multiple trials of the simulate_cache.run_simulation() to collect mean and std metrics.
Writes sim_summary.svg and sim_summary.json and prints the aggregated results.
"""
import importlib
import json
import statistics
from pathlib import Path

RESULT_JSON = Path('sim_summary.json')
RESULT_SVG = Path('sim_summary.svg')

def run_trials(n_trials=5):
    # import the simulate_cache module fresh each trial to avoid accidental state reuse
    results = []
    for t in range(n_trials):
        mod = importlib.import_module('simulate_cache')
        importlib.reload(mod)
        # run smaller trials for speed during aggregation
        lru, lfu, pred = mod.run_simulation(num_keys=2000, seq_len=20000, cache_capacity=400, quiet=True)
        results.append({'lru': lru, 'lfu': lfu, 'pred': pred})
    return results

def aggregate(results):
    def collect(role, idx):
        return [r[role][idx] for r in results]

    agg = {}
    for role in ('lru','lfu','pred'):
        hit_rates = collect(role, 0)
        latencies = collect(role, 1)
        agg[role] = {
            'hit_mean': statistics.mean(hit_rates),
            'hit_std': statistics.stdev(hit_rates) if len(hit_rates) > 1 else 0.0,
            'lat_mean': statistics.mean(latencies),
            'lat_std': statistics.stdev(latencies) if len(latencies) > 1 else 0.0,
        }
    return agg

def write_json(agg):
    with RESULT_JSON.open('w', encoding='utf-8') as f:
        json.dump(agg, f, indent=2)

def write_svg(agg):
    # Simple SVG showing mean hit rates with error bars
    svg_w = 800
    svg_h = 200
    margin = 40
    bar_w = 80
    gap = 60
    policies = ['LRU','LFU','Predictive']
    means = [agg['lru']['hit_mean'], agg['lfu']['hit_mean'], agg['pred']['hit_mean']]
    stds = [agg['lru']['hit_std'], agg['lfu']['hit_std'], agg['pred']['hit_std']]
    svg = [f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<style>text { font-family: Arial; font-size: 12px; }</style>')
    max_h = max(means) if means else 1
    for i, m in enumerate(means):
        x = margin + i * (bar_w + gap)
        h = (svg_h - 2*margin) * m
        y = svg_h - margin - h
        svg.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" fill="#1f77b4"/>')
        # error bar
        err = stds[i]
        err_h = (svg_h - 2*margin) * err
        cx = x + bar_w/2
        svg.append(f'<line x1="{cx}" y1="{y - err_h}" x2="{cx}" y2="{y + h + err_h}" stroke="#000"/>')
        svg.append(f'<text x="{cx}" y="{y - err_h - 6}" text-anchor="middle">{m:.3f}±{err:.3f}</text>')
        svg.append(f'<text x="{x + bar_w/2}" y="{svg_h - margin + 16}" text-anchor="middle">{policies[i]}</text>')
    svg.append('</svg>')
    RESULT_SVG.write_text('\n'.join(svg), encoding='utf-8')

def main():
    n = 5
    print(f'Running {n} trials...')
    results = run_trials(n)
    agg = aggregate(results)
    write_json(agg)
    write_svg(agg)
    print('Aggregated results:')
    for k,v in agg.items():
        print(f'{k}: hit {v["hit_mean"]:.4f} ± {v["hit_std"]:.4f}, lat {v["lat_mean"]:.2f} ± {v["lat_std"]:.2f}')

if __name__ == "__main__":
    main()
