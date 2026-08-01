#!/usr/bin/env python3
"""FASE 1 · Bootstrap por LENGUA de C(O) (revisión: la unidad válida, no el soporte por-pareja).

C(O) es un U-statistic sobre pares de operadores NO independientes; el bootstrap correcto resamplea la unidad de
observación — la LENGUA — con reemplazo, recorre el pipeline idéntico (LexStat + alineamiento) y recomputa C(O).
Guarda cada iteración en un archivo (resumible) e imprime IC percentil al final. Costoso: 1 corrida LexStat por
iteración. Uso: TF_FAMILY="Indo-European" TF_B=40 python3 src/bootstrap_lang.py
"""
import logging; logging.disable(logging.INFO)
import os, csv, sqlite3, random
from collections import defaultdict
import panphon
from lingpy import LexStat

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MAXLANG = int(os.environ.get("TF_MAXLANG", "30"))
MINEDGE = int(os.environ.get("TF_MINEDGE", "30"))
B = int(os.environ.get("TF_B", "40"))
THR = 0.55
OUT = os.path.join(HERE, "..", "data", "db", f"_bootlang_{FAMILY.replace(' ','_')}.txt")
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
FT = panphon.FeatureTable(); _vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def is_cons(ph):
    f = feat(ph); return f is not None and f.get("syl", 0) != 1


def delta(a, b):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None: return None
    d = frozenset(k for k in PRIM if fa.get(k, 0) != fb.get(k, 0))
    return d if 0 < len(d) <= 3 else None


def cost(a, b):
    if a == b: return 0.0
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None: return 1.0
    return sum(1 for k in FT.names if fa.get(k, 0) != fb.get(k, 0)) / len(FT.names)


def align(s, t):
    n, m = len(s), len(t)
    D = [[0.0]*(m+1) for _ in range(n+1)]
    for i in range(1, n+1): D[i][0] = i
    for j in range(1, m+1): D[0][j] = j
    for i in range(1, n+1):
        for j in range(1, m+1):
            D[i][j] = min(D[i-1][j-1]+cost(s[i-1], t[j-1]), D[i-1][j]+1, D[i][j-1]+1)
    out, i, j = [], n, m
    while i > 0 and j > 0:
        if abs(D[i][j]-(D[i-1][j-1]+cost(s[i-1], t[j-1]))) < 1e-9:
            out.append((s[i-1], t[j-1])); i -= 1; j -= 1
        elif abs(D[i][j]-(D[i-1][j]+1)) < 1e-9: i -= 1
        else: j -= 1
    return out[::-1]


def cofO(O):
    O = list(O); s = set(O); n = len(O); real = 0
    for i in range(n):
        for j in range(i+1, n):
            if (O[i] ^ O[j]) in s: real += 1
    return real / (n*(n-1)//2) if n > 1 else 0.0


def repertoire(doculect_forms):
    """doculect_forms: dict doculect_id -> list of (concept, segs). LexStat → O (deltas soporte≥MINEDGE)."""
    tsv = os.path.join(HERE, "..", "data", "db", f"_bl_{FAMILY.replace(' ','_')}.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1
        for doc, forms in doculect_forms.items():
            for concept, segs in forms:
                f.write(f"{i}\t{doc}\t{concept}\t{' '.join(segs)}\n"); i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")
    by = defaultdict(lambda: defaultdict(list))
    for k in lex:
        by[lex[k, "concept"]][lex[k, "cogid"]].append((lex[k, "doculect"], lex[k, "tokens"]))
    raw = defaultdict(int)
    for concept, classes in by.items():
        for cid, forms in classes.items():
            for x in range(len(forms)):
                for y in range(x+1, len(forms)):
                    if forms[x][0] == forms[y][0]: continue
                    for a, b in align(forms[x][1], forms[y][1]):
                        if a != b and is_cons(a) and is_cons(b):
                            d = delta(a, b)
                            if d: raw[d] += 1
    return [d for d, c in raw.items() if c >= MINEDGE]


def load_pool():
    lang_fam = {r["ID"]: (r.get("Family") or "") for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    per = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        if lang_fam.get(row["Language_ID"]) != FAMILY: continue
        segs = (row.get("Segments") or "").split()
        if len(segs) >= 2 and row.get("Parameter_ID"):
            per[row["Language_ID"]].append((row["Parameter_ID"], segs))
    return {l: per[l] for l in sorted(per, key=lambda x: -len(per[x]))[:MAXLANG]}


def main():
    rng = random.Random(2024)
    pool = load_pool()
    langs = list(pool)
    # punto estimado (pool completo)
    C_obs = cofO(repertoire({l: pool[l] for l in langs}))
    with open(OUT, "w") as f:
        f.write(f"# {FAMILY} language-bootstrap C(O); obs={C_obs:.4f}; pool={len(langs)}; B={B}\n")
    print(f"[{FAMILY}] C(O) obs = {C_obs:.4f} (pool {len(langs)} langs). Running {B} language-resamples…", flush=True)
    boots = []
    for b in range(B):
        sample = [rng.choice(langs) for _ in range(len(langs))]      # resample langs WITH replacement
        docs = {}
        for k, l in enumerate(sample):
            docs[f"{l}__c{k}"] = pool[l]                              # duplicated language = distinct doculect
        c = cofO(repertoire(docs))
        boots.append(c)
        with open(OUT, "a") as f:
            f.write(f"{c:.4f}\n")
        print(f"  iter {b+1}/{B}: C={c:.4f}", flush=True)
    boots.sort()
    lo, hi = boots[int(0.025*len(boots))], boots[int(0.975*len(boots))]
    mean = sum(boots)/len(boots)
    with open(OUT, "a") as f:
        f.write(f"# obs={C_obs:.4f} mean={mean:.4f} CI95=[{lo:.4f},{hi:.4f}]\n")
    print(f"\n=== {FAMILY} · language-level bootstrap of C(O) ===")
    print(f"obs={C_obs:.4f}  mean={mean:.4f}  CI95=[{lo:.4f},{hi:.4f}]  (B={B}, resampling unit = language)")


if __name__ == "__main__":
    main()
