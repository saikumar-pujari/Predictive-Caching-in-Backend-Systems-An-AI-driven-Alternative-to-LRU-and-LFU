"""
Build a submission bundle (zip) containing:
- paper.pdf (if it exists) or paper.md
- all code files in this folder
- results (sim_results.svg, sim_summary.svg, sim_summary.json)
- README and submission_instructions.txt

Usage: python build_submission.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / 'submission_bundle.zip'
INCLUDE = ['paper.md', 'paper_humanized.md', 'README.md', 'submission_instructions.txt', 'simulate_cache.py', 'run_simulations.py', 'sim_results.svg', 'sim_summary.svg', 'sim_summary.json', 'tests']

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    # prefer paper.pdf if present
    if (ROOT / 'paper.pdf').exists():
        z.write(ROOT / 'paper.pdf', 'paper.pdf')
    else:
        z.write(ROOT / 'paper.md', 'paper.md')
    for item in INCLUDE:
        p = ROOT / item
        if p.exists():
            if p.is_dir():
                for f in p.rglob('*'):
                    z.write(f, f.relative_to(ROOT))
            else:
                z.write(p, p.name)

print('Created', OUT)
