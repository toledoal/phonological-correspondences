#!/usr/bin/env python3
"""Figura TikZ del GRAFO DE LENGUAS G_L (Cap. 21): nodos = lenguas (color = rama Glottolog), aristas = vecinos
más cercanos por distancia entre sus DISTRIBUCIONES de operadores.

Cada lengua recibe un vector de frecuencia sobre los tipos de operador (de las correspondencias en que participa);
la distancia entre dos lenguas es la divergencia de Jensen–Shannon de esos vectores. Conectamos cada lengua a sus
2 vecinos más cercanos. Si el grafo se agrupa por color (rama) SIN habérselo dicho, la genealogía emerge de la
sola distribución de operadores (conecta con family-blind, Cap. 18). Uso: TF_FAMILY="..." python3 src/fig_langgraph.py > fig-langgraph-ie.tex
"""
import logging; logging.disable(logging.INFO)
import os, csv, math
from collections import defaultdict, Counter
import panphon, networkx as nx
from lingpy import LexStat
from branches import branch_map

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MAXLANG = int(os.environ.get("TF_LGNODES", "18"))
THR = 0.55
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
FT = panphon.FeatureTable(); _vc = {}
PALETTE = ["NavyBlue", "BurntOrange", "ForestGreen", "Purple", "Sepia", "Red", "Teal", "Magenta",
           "Brown", "OliveGreen", "RoyalBlue", "Mahogany"]


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


def js(p, q, vocab):
    def norm(d):
        t = sum(d.get(k, 0) for k in vocab) or 1
        return {k: d.get(k, 0)/t for k in vocab}
    P, Q = norm(p), norm(q)
    M = {k: 0.5*(P[k]+Q[k]) for k in vocab}
    def kl(A, B):
        return sum(A[k]*math.log2(A[k]/B[k]) for k in vocab if A[k] > 0 and B[k] > 0)
    return 0.5*kl(P, M) + 0.5*kl(Q, M)


def main():
    assign, _, _ = branch_map(FAMILY)
    lang_fam = {r["ID"]: (r.get("Family") or "") for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    lang_name = {r["ID"]: (r.get("Name") or r["ID"]) for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    per = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        if lang_fam.get(row["Language_ID"]) != FAMILY: continue
        segs = (row.get("Segments") or "").split()
        if len(segs) >= 2 and row.get("Parameter_ID") and assign.get(row["Language_ID"]):
            per[row["Language_ID"]].append((row["Parameter_ID"], segs))
    langs = sorted(per, key=lambda l: -len(per[l]))[:MAXLANG]
    tsv = os.path.join(HERE, "..", "data", "db", "_lg.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1
        for l in langs:
            for c, segs in per[l]:
                f.write(f"{i}\t{l}\t{c}\t{' '.join(segs)}\n"); i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")
    classes = defaultdict(list)
    for k in lex:
        classes[(lex[k, "concept"], lex[k, "cogid"])].append((lex[k, "doculect"], lex[k, "tokens"]))
    vec = defaultdict(Counter)
    for _, forms in classes.items():
        for x in range(len(forms)):
            for y in range(x+1, len(forms)):
                la, sa = forms[x]; lb, sb = forms[y]
                if la == lb: continue
                for a, b in align(sa, sb):
                    if a != b and is_cons(a) and is_cons(b):
                        d = delta(a, b)
                        if d:
                            key = "+".join(sorted(d))
                            vec[la][key] += 1; vec[lb][key] += 1
    langs = [l for l in langs if vec[l]]
    vocab = sorted({k for l in langs for k in vec[l]})
    G = nx.Graph()
    for l in langs: G.add_node(l)
    for a in langs:                                  # cada lengua → sus 2 vecinos más cercanos
        ds = sorted(((js(vec[a], vec[b], vocab), b) for b in langs if b != a))
        for _, b in ds[:2]:
            G.add_edge(a, b)
    pos = nx.spring_layout(G, seed=7, k=1.9, iterations=300)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    sx = 11.0/(max(xs)-min(xs)+1e-9); sy = 6.6/(max(ys)-min(ys)+1e-9)
    brs = sorted({assign[l] for l in langs})
    col = {b: PALETTE[i % len(PALETTE)] for i, b in enumerate(brs)}

    out = [r"\begin{figure}[htbp]\centering", r"\begin{tikzpicture}[font=\scriptsize]"]
    ids = {l: f"L{i}" for i, l in enumerate(langs)}
    for l, (x, y) in pos.items():
        c = col[assign[l]]
        nm = lang_name[l].replace("&", "\\&")[:14]
        out.append(f"\\node[circle,draw={c},fill={c}!15,line width=0.7pt,inner sep=1pt] ({ids[l]}) "
                   f"at ({(x-min(xs))*sx-5.5:.2f},{(y-min(ys))*sy-3.3:.2f}) {{}};")
        out.append(f"\\node[font=\\tiny,{c},anchor=west] at ({(x-min(xs))*sx-5.35:.2f},{(y-min(ys))*sy-3.3:.2f}) {{{nm}}};")
    for a, b in G.edges():
        out.append(f"\\draw[gray,opacity=0.5,line width=0.4pt] ({ids[a]}) -- ({ids[b]});")
    out.append(r"\end{tikzpicture}")
    legend = ", ".join(f"\\textcolor{{{col[b]}}}{{{b}}}" for b in brs)
    out.append(r"\caption{\textbf{Language graph $G_L$ of " + FAMILY + r".} Each node is a language, coloured by "
               r"its Glottolog branch; two languages are joined when one is among the other's two nearest "
               r"neighbours in \emph{operator-distribution} distance (Jensen--Shannon). Colour was \emph{not} used "
               r"to build the graph --- only the operator frequencies were. Whether same-colour nodes cluster is a "
               r"visual test of how much genealogy the distributions alone carry (cf.\ Chapters 14, 18). Branches: "
               + legend + r".}")
    out.append(r"\end{figure}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
