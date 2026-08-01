# Results store — durable, reusable experiment outputs

Numeric results from expensive or stochastic runs are persisted here so they need not be recomputed and can
feed later experiments. Two coordinated forms:

1. **CSV per experiment** (`*.csv`, committed) — human-readable, one row per observation, with the run
   parameters in the header/columns (family, B, MAXLANG, MINEDGE, seed, threshold). Easy to load in pandas/R.
2. **Table in `../db/transf.db`** (queryable, ships with the repo) — the same rows plus a `run_meta` record
   (timestamp, git commit, parameters), so downstream scripts can `SELECT` results by experiment and parameters.

Convention: raw per-iteration values are kept (not just summaries), so future work can recompute CIs with a
different method (BCa, jackknife), pool across runs, or study the full distribution — not only the point summary.

Current contents:
- `bootstrap_lang.csv` — language-level bootstrap of C(O) (per-iteration C, + obs/mean/CI per family).
