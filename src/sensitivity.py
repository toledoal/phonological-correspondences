#!/usr/bin/env python3
"""FASE 1 · Análisis de sensibilidad (revisión: los titulares deben ser invariantes a las decisiones de medición).

Barre las tres decisiones que el paper declara como instrumentos de medición y verifica que los SIGNOS de los
resultados centrales no dependen de ellas:
  (1) umbral de soporte MINEDGE  (2) cap de peso de operador  (3) subconjunto de rasgos.
Corre sobre data/db/transf.db (empaquetado; sin corpora). Uso: TF_FAMILY="Indo-European" python3 src/sensitivity.py
"""
import os, sqlite3, itertools
import panphon
from algebra import gf2_rank

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
FULL = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
FT = panphon.FeatureTable(); _vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def is_cons(ph):
    f = feat(ph); return f is not None and f.get("syl", 0) != 1


def delta(a, b, feats, cap):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None: return None
    d = frozenset(k for k in feats if fa.get(k, 0) != fb.get(k, 0))
    return d if 0 < len(d) <= cap else None


def rows():
    con = sqlite3.connect(DB)
    r = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    return [(a, b, c) for a, b, c in r if a != b and is_cons(a) and is_cons(b)]


def build_O(rws, feats, cap, minedge):
    O = set()
    for a, b, c in rws:
        if c >= minedge:
            d = delta(a, b, feats, cap)
            if d: O.add(d)
    return list(O)


def rank_of(O, feats):
    used = [r for r in feats if any(r in d for d in O)]
    idx = {r: i for i, r in enumerate(used)}
    return gf2_rank([sum(1 << idx[r] for r in d) for d in O])


def cofO(O):
    s = set(O); n = len(O); real = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (O[i] ^ O[j]) in s: real += 1
    return real / (n * (n - 1) // 2) if n > 1 else 0.0


def opp_occ(O, rws, feats, cap):
    """ocupación vs oportunidad: |O| / |Ω_D ∩ span(O)|, Ω_D = deltas con soporte≥1."""
    Omega = set()
    for a, b, c in rws:
        d = delta(a, b, feats, cap)
        if d: Omega.add(d)
    # span membership
    used = [r for r in feats if any(r in d for d in O)]
    idx = {r: i for i, r in enumerate(used)}
    basis = []
    for d in O:
        v = sum(1 << idx[r] for r in d if r in idx)
        for b_ in basis: v = min(v, v ^ b_)
        if v: basis.append(v); basis.sort(reverse=True)
    def in_span(d):
        if any(r not in idx for r in d): return False
        v = sum(1 << idx[r] for r in d);
        for b_ in basis: v = min(v, v ^ b_)
        return v == 0
    Om_in = [d for d in Omega if in_span(d)]
    return len(O) / max(1, len(Om_in))


def main():
    rws = rows()
    print(f"\n=== FASE 1 · Sensibilidad · {FAMILY} ===")

    print("\n(1) UMBRAL DE SOPORTE (feats=12, cap=3):")
    print(f"   {'MINEDGE':>8} {'|O|':>5} {'rank':>5} {'atoms':>6} {'C(O)':>7} {'rho_opp':>8}")
    for me in [15, 20, 30, 40, 60]:
        O = build_O(rws, FULL, 3, me)
        atoms = sum(1 for d in O if len(d) == 1)
        print(f"   {me:>8} {len(O):>5} {rank_of(O, FULL):>5} {atoms:>6} {cofO(O):>7.3f} {opp_occ(O, rws, FULL, 3):>8.3f}")

    print("\n(2) CAP DE PESO DE OPERADOR (feats=12, MINEDGE=30):")
    print(f"   {'cap<=':>6} {'|O|':>5} {'rank':>5} {'C(O)':>7}")
    for cap in [2, 3, 4]:
        O = build_O(rws, FULL, cap, 30)
        print(f"   {cap:>6} {len(O):>5} {rank_of(O, FULL):>5} {cofO(O):>7.3f}")

    print("\n(3) SUBCONJUNTO DE RASGOS (cap=3, MINEDGE=30):")
    variants = {
        "full-12": FULL,
        "sin lab": [f for f in FULL if f != "lab"],
        "sin round,lo": [f for f in FULL if f not in ("round", "lo")],
        "manner+voi+place (8)": ["cont", "voi", "nas", "strid", "son", "ant", "cor", "back"],
    }
    print(f"   {'variante':>22} {'|O|':>5} {'rank':>5} {'C(O)':>7}")
    for name, fs in variants.items():
        O = build_O(rws, fs, 3, 30)
        print(f"   {name:>22} {len(O):>5} {rank_of(O, fs):>5} {cofO(O):>7.3f}")

    print("\nLectura: si a lo largo de cada barrido |O| y el rango varían suavemente pero C(O) y rho_opp se")
    print("mantienen claramente por encima del suelo (~0.12–0.15 del nulo), los TITULARES son invariantes a la")
    print("decisión de medición — que es lo que el análisis de sensibilidad debe mostrar.")


if __name__ == "__main__":
    main()
