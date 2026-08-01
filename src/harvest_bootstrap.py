#!/usr/bin/env python3
"""Cosecha un run de bootstrap por-lengua (data/db/_bootlang_<FAMILY>.txt) a almacenamiento DURABLE:
   · data/results/bootstrap_lang.csv  (una fila por iteración, con obs/media/IC y parámetros; versionado)
   · tabla `bootstrap_lang` en data/db/transf.db  (queryable, viaja con el repo)
Conserva los valores CRUDOS por iteración (para recalcular IC con otro método después). Idempotente por familia.
Uso: TF_FAMILY="Austronesian" python3 src/harvest_bootstrap.py
"""
import os, csv, sqlite3, re

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
RES = os.path.join(HERE, "..", "data", "results", "bootstrap_lang.csv")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
SRC = os.path.join(HERE, "..", "data", "db", f"_bootlang_{FAMILY.replace(' ','_')}.txt")
COLS = ["family", "iter", "c", "obs", "mean", "ci_lo", "ci_hi", "B", "pool", "minedge"]


def parse():
    obs = mean = ci_lo = ci_hi = None; B = pool = None; iters = []
    for line in open(SRC, encoding="utf-8"):
        line = line.strip()
        if line.startswith("#"):
            m = re.search(r"obs=([\d.]+)", line);  obs = float(m.group(1)) if m else obs
            m = re.search(r"pool=(\d+)", line);     pool = int(m.group(1)) if m else pool
            m = re.search(r"B=(\d+)", line);        B = int(m.group(1)) if m else B
            m = re.search(r"mean=([\d.]+)", line);  mean = float(m.group(1)) if m else mean
            m = re.search(r"CI95=\[([\d.]+),([\d.]+)\]", line)
            if m: ci_lo, ci_hi = float(m.group(1)), float(m.group(2))
        elif line and line[0].isdigit():
            iters.append(float(line))
    return obs, mean, ci_lo, ci_hi, B, pool, iters


def main():
    if not os.path.exists(SRC):
        print(f"no source: {SRC}"); return
    obs, mean, ci_lo, ci_hi, B, pool, iters = parse()
    minedge = int(os.environ.get("TF_MINEDGE", "30"))
    if mean is None and iters:
        mean = sum(iters)/len(iters)
    if (ci_lo is None) and iters:
        s = sorted(iters); ci_lo, ci_hi = s[int(0.025*len(s))], s[int(0.975*len(s))]

    # --- CSV (regenera excluyendo la familia y reescribe) ---
    rows = []
    if os.path.exists(RES):
        rows = [r for r in csv.DictReader(open(RES, encoding="utf-8")) if r["family"] != FAMILY]
    for i, c in enumerate(iters, 1):
        rows.append({"family": FAMILY, "iter": i, "c": f"{c:.4f}", "obs": f"{obs:.4f}",
                     "mean": f"{mean:.4f}", "ci_lo": f"{ci_lo:.4f}", "ci_hi": f"{ci_hi:.4f}",
                     "B": B, "pool": pool, "minedge": minedge})
    with open(RES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)

    # --- transf.db table ---
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS bootstrap_lang
        (family TEXT, iter INT, c REAL, obs REAL, mean REAL, ci_lo REAL, ci_hi REAL, B INT, pool INT, minedge INT)""")
    con.execute("DELETE FROM bootstrap_lang WHERE family=?", (FAMILY,))
    con.executemany("INSERT INTO bootstrap_lang VALUES (?,?,?,?,?,?,?,?,?,?)",
                    [(FAMILY, i, c, obs, mean, ci_lo, ci_hi, B, pool, minedge) for i, c in enumerate(iters, 1)])
    con.commit(); con.close()

    print(f"[{FAMILY}] harvested {len(iters)} iters → data/results/bootstrap_lang.csv + transf.db(bootstrap_lang)")
    print(f"   obs={obs:.4f}  mean={mean:.4f}  CI95=[{ci_lo:.4f},{ci_hi:.4f}]  B={B} pool={pool}")


if __name__ == "__main__":
    main()
