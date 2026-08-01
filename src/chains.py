#!/usr/bin/env python3
"""X4 · Cadenas preferentes (corredores de cambio) DENTRO de un sistema — transformations.

Un corredor es un camino en el grafo de correspondencias donde cada paso AVANZA monótonamente en UNA dimensión
(p.ej. constricción: oclusiva→africada→fricativa→∅, el clásico t→ts→s; o retracción: velar→uvular). Como las
correspondencias son simétricas (reconstrucción-libre), la monotonía en la dimensión da la ORIENTACIÓN geométrica
del corredor sin presuponer dirección histórica. Buscamos los corredores más pesados (más transitados) por
dimensión.

Entrada: transf.db (lex_correspondence). Uso: TF_FAMILY="Indo-European" python3 src/chains.py
"""
import os, sqlite3
from collections import defaultdict
import panphon

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MINEDGE = 25
FT = panphon.FeatureTable()
_vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def is_cons(ph):
    f = feat(ph); return f is not None and f.get("syl", 0) != 1


def stricture(ph):
    """escala de constricción: oclusiva0 < africada1 < fricativa2 < aproximante/líquida3."""
    f = feat(ph)
    if f is None: return None
    if f.get("son", 0) == 1: return 3
    if f.get("cont", 0) == 1: return 2
    if f.get("delrel", 0) == 1: return 1
    return 0


def backness(ph):
    """lugar de adelante hacia atrás: labial/coronal0 < palatal1 < velar2 < uvular/faríngeo3."""
    f = feat(ph)
    if f is None: return None
    if f.get("back", 0) == 1 and f.get("hi", 0) != 1: return 3   # uvular/faríngeo
    if f.get("back", 0) == 1: return 2                            # velar
    if f.get("hi", 0) == 1 and f.get("cor", 0) == 1: return 1     # palatal
    return 0                                                      # labial/coronal


DIMS = [("constricción (oclusiva→africada→fricativa→aproximante)", stricture),
        ("retracción (labial/coronal→palatal→velar→uvular)", backness)]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    W = defaultdict(int)
    for a, b, c in rows:
        if a != b and c >= MINEDGE and is_cons(a) and is_cons(b):
            W[frozenset((a, b))] += c
    nodes = set()
    for e in W:
        nodes |= set(e)

    print(f"\n=== Cadenas preferentes (corredores de cambio) en {FAMILY} ===\n")
    for name, rank in DIMS:
        # DAG dirigido: a→b si hay correspondencia y rank sube estrictamente
        succ = defaultdict(list)
        for e, w in W.items():
            a, b = tuple(e)
            ra, rb = rank(a), rank(b)
            if ra is None or rb is None or ra == rb:
                continue
            lo, hi = (a, b) if ra < rb else (b, a)
            succ[lo].append((hi, w))
        # camino de MÁS peso (DP sobre el DAG por rango)
        best = {n: (W_ if False else 0, [n]) for n in nodes}
        for n in sorted(nodes, key=lambda x: rank(x) or 0):
            for nx, w in succ.get(n, []):
                cand = best[n][0] + w
                if cand > best[nx][0] and n not in best[nx][1]:
                    best[nx] = (cand, best[n][1] + [nx])
        paths = sorted((v for v in best.values() if len(v[1]) >= 3), key=lambda x: -x[0])
        print(f"● {name}:")
        if not paths:
            print("   (sin corredores de ≥3 pasos)\n"); continue
        seen = set()
        shown = 0
        for w, p in paths:
            key = tuple(p)
            if key in seen: continue
            seen.add(key)
            # peso mínimo de un tramo (cuello del corredor)
            steps = " → ".join(p)
            bottleneck = min(W[frozenset((p[i], p[i+1]))] for i in range(len(p)-1))
            print(f"   {steps}   (peso total {w}, tramo más débil {bottleneck})")
            shown += 1
            if shown >= 4: break
        print()
    print("Lectura: son corredores GEOMÉTRICOS (monótonos en una dimensión), no direcciones históricas afirmadas —")
    print("los caminos por donde el sistema efectivamente mueve sus segmentos, paso a paso.")


if __name__ == "__main__":
    main()
