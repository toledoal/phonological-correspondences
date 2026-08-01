#!/usr/bin/env python3
"""Genera una figura TikZ del grafo de operadores de un sistema (desde lex_correspondence).

Nodos = segmentos; aristas = correspondencias sistemáticas (con cambio de rasgo), coloreadas por el TIPO de
cambio dominante (sonoridad / fricativización / palatalización / lugar / prenasalización). Layout de resorte
(networkx). Uso: TF_FAMILY="Indo-European" python3 src/fig_graph.py > docs/fig-graph.tex
"""
import os, sqlite3, sys, math
import panphon, networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
TOPEDGES = int(os.environ.get("TF_EDGES", "26"))
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
FT = panphon.FeatureTable()
_vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def is_cons(ph):
    f = feat(ph); return f is not None and f.get("syl", 0) != 1


def dset(a, b):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None: return None
    d = frozenset(k for k in PRIM if fa.get(k, 0) != fb.get(k, 0))
    return d if 0 < len(d) <= 3 else None


def color(d):
    if "voi" in d and "nas" in d: return "Purple"       # prenasalización
    if "voi" in d: return "NavyBlue"                     # sonoridad
    if "cont" in d or "strid" in d: return "BurntOrange" # fricativización/lenición
    if "hi" in d: return "ForestGreen"                   # palatalización/altura
    if "ant" in d or "cor" in d or "back" in d: return "Sepia"  # lugar
    return "Gray"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    G = nx.Graph()
    for a, b, c in rows:
        if a == b or not (is_cons(a) and is_cons(b)): continue
        d = dset(a, b)
        if d is None: continue
        G.add_edge(a, b, w=c, d=d)
    flux = dict(G.degree(weight="w"))
    N = sum(d["w"] for *_, d in G.edges(data=True)) * 2
    scored = sorted(G.edges(data=True), key=lambda e: -math.log2(e[2]["w"] * N / (flux[e[0]] * flux[e[1]])))
    top = scored[:TOPEDGES]
    H = nx.Graph()
    for a, b, d in top:
        H.add_edge(a, b, **d)
    pos = nx.spring_layout(H, seed=3, k=1.4, iterations=200)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    sx, sy = 11.0 / (max(xs) - min(xs) + 1e-9), 6.5 / (max(ys) - min(ys) + 1e-9)

    out = [r"\begin{figure}[htbp]\centering", r"\begin{tikzpicture}[font=\small]"]
    for n, (x, y) in pos.items():
        out.append(f"\\node[circle,draw,fill=black!4,inner sep=1.4pt] (N{abs(hash(n))%100000}) "
                   f"at ({(x-min(xs))*sx-5.5:.2f},{(y-min(ys))*sy-3.2:.2f}) {{\\texttt{{{n}}}}};")
    ids = {n: f"N{abs(hash(n))%100000}" for n in pos}
    for a, b, d in top:
        col = color(d["d"])
        lw = 0.4 + min(2.0, d["w"] / 4000)
        out.append(f"\\draw[{col},line width={lw:.1f}pt,opacity=0.75] ({ids[a]}) -- ({ids[b]});")
    out.append(r"\end{tikzpicture}")
    out.append(r"\caption{\textbf{Segmental correspondence graph $G_S$ of " + FAMILY + r".} Nodes are segments; "
               r"edges are recurrent correspondences, with thickness $\propto$ frequency and colour by change "
               r"type: \textcolor{NavyBlue}{voicing}, \textcolor{BurntOrange}{fricativization/lenition}, "
               r"\textcolor{ForestGreen}{palatalization/height}, \textcolor{Sepia}{place}, "
               r"\textcolor{Purple}{prenasalization}.}")
    out.append(r"\end{figure}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
