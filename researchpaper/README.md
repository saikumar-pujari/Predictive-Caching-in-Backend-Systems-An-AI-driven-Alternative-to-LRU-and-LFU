# Predictive Caching — repository guide

This folder contains the paper (Markdown + PDF), a pure-Python simulator, tests, and reproducible artifacts used to evaluate simple cache policies (LRU, LFU, and a small heuristic predictor).

Goal of this README
- Tell you which files to upload to GitHub for reviewers and reproducibility
- Show a recommended repository layout and reading order
- Provide copy-paste commands for Windows (cmd) to push the code and release the supplementary ZIP

Recommended files to upload (minimum set)
- `paper.md` — the human-readable paper (Markdown).
- `paper.pdf` — the single-file PDF ready for submission (best when it embeds figures).
- `submission_bundle.zip` — a ZIP containing code, tests, raw simulation outputs and instructions.
- `simulate_cache.py` — the simulator (pure-Python, dependency-light).
- `run_simulations.py` — runner for multiple quick trials and aggregation.
- `tests/` — unit tests (ensure reproducibility and CI friendliness).
- `README.md` — this file (explain repo layout and how to reproduce).

Optional but useful
- `paper_humanized.md` — first-person rewrite used during drafting.
- `sim_results.svg`, `sim_summary.svg`, `sim_summary.json` — generated figures and summary results.
- `architecture.svg` — a simple architecture diagram.

Suggested repository layout (root of new repo)

```
<repo-root>/
	README.md                # Top-level README for the repo (short description + link to researchpaper/)
	researchpaper/
		paper.pdf
		paper.md
		paper_humanized.md
		simulate_cache.py
		run_simulations.py
		md_to_pdf_fallback.py
		build_submission.py
		submission_bundle.zip
		sim_results.svg
		sim_summary.svg
		sim_summary.json
		architecture.svg
		tests/
			test_simulator.py
			test_simulator_extended.py
		README.md              # this file, focused on reproduction and submission
```

Reading order (what reviewers or you should open first)
1. `paper.pdf` — the submission-ready PDF containing the writeup and short appendix.
2. `README.md` (repo root) — high-level overview and link to `researchpaper/`.
3. `researchpaper/README.md` (this) — step-by-step reproduction instructions and files list.
4. `submission_bundle.zip` (or the repo itself) — contains the code and raw outputs.
5. `simulate_cache.py` and `run_simulations.py` — inspect and run the simulator.
6. `tests/` — run unit tests to verify reproducibility.

How to push this folder to GitHub (Windows cmd) — copy & paste

1) Create a new repository on GitHub (web UI) named e.g. `predictive-cache-paper`.

2) From this `researchpaper/` folder, run these commands (replace <your-username> and <repo-name>):

```cmd
cd %USERPROFILE%\Desktop\vsc\fuck-ya\researchpaper
git init
git add .
git commit -m "Add paper, code, simulations, and tests"
git remote add origin https://github.com\<your-username>\<repo-name>.git
git branch -M main
git push -u origin main
```

3) Upload `submission_bundle.zip` as a release asset (recommended):

	- Go to the GitHub repo → Releases → Draft a new release → attach `submission_bundle.zip` → Publish release.

Alternative: Using GitHub web UI upload
- You can upload files directly using the web interface by creating the repo and clicking "Add file" → "Upload files".

README and how to read files (short guide for reviewers)
- Paper: read `paper.pdf` first — it has the summary, methods, evaluation, and appendix with reproduction steps.
- Reproduce: download `submission_bundle.zip` (or clone the repo), follow the README in `researchpaper/` to run `simulate_cache.py` and the tests.
- Inspect code: the simulator is intentionally simple and dependency-light. Read `simulate_cache.py` for the policies and `run_simulations.py` for the experiment harness.

Notes and tips
- If your paper PDF currently lacks embedded images, generate a new PDF locally with Pandoc + XeLaTeX or use VS Code's Export → PDF command to include images.
- Keep the repo tidy: avoid committing large binaries that aren't needed; `submission_bundle.zip` as a release asset is appropriate for reviewers.
- If you want, add a short CITATION or README that points to your personal website or a DOI if you later publish.

If you'd like, I can also:
- Create a small `push_to_github.cmd` file with the exact commands (placeholders replaced) to make pushing trivial.
- Create a short `CONTRIBUTING.md` and license file.

---
Updated to include a recommended upload list and reading order. If you want a ready-to-run Windows .cmd script to push the repository and create a release, tell me and I'll add it with placeholders for your repo name.
