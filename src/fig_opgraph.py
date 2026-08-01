#!/usr/bin/env python3
"""Figura TikZ del GRAFO DE OPERADORES G_O (Cap. 21): nodos = operadores, arista u–v cuando u⊕v ∈ O.

Es el grafo de la estructura ADITIVA (Cap. 10-11): dos operadores están conectados si su composición vuelve a ser
un operador del repertorio. Tamaño de nodo ∝ soporte; color por tipo de cambio dominante. Se muestran los
operadores de mayor soporte para que sea legible. Uso: TF_FAMILY="Indo-European" python3 src/fig_opgraph.py > fig-opgraph-ie.tex
"""
import os, sqlite3, math
import panphon, networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
TOPN = int(os.environ.get("TF_OPNODES", "22"))
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


def color(d):
    if "voi" in d and "nas" in d: return "Purple"
    if "voi" in d: return "NavyBlue"
    if "cont" in d or "strid" in d: return "BurntOrange"
    if "hi" in d: return "ForestGreen"
    if "ant" in d or "cor" in d or "back" in d or "lab" in d: return "Sepia"
    return "Gray"


def lab(d):
    return "{" + "+".join(sorted(d)) + "}"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    supp = {}
    for a, b, c in rows:
        if a != b and c >= 30 and is_cons(a) and is_cons(b):
            d = delta(a, b)
            if d:
                supp[d] = supp.get(d, 0) + c
    ops = set(supp)
    top = sorted(ops, key=lambda d: -supp[d])[:TOPN]
    topset = set(top)
    G = nx.Graph()
    for d in top:
        G.add_node(d)
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            if (top[i] ^ top[j]) in ops:            # composición cae en el repertorio (arista aditiva)
                G.add_edge(top[i], top[j])
    pos = nx.spring_layout(G, seed=5, k=1.6, iterations=250)
    xs = [p[0] for p in pos.values()]; ys = [p[1] for p in pos.values()]
    sx = 11.0 / (max(xs) - min(xs) + 1e-9); sy = 6.6 / (max(ys) - min(ys) + 1e-9)
    mx = max(supp[d] for d in top)

    out = [r"\begin{figure}[htbp]\centering", r"\begin{tikzpicture}[font=\scriptsize]"]
    ids = {d: f"P{i}" for i, d in enumerate(top)}
    for d, (x, y) in pos.items():
        r = 0.10 + 0.34 * (supp[d] / mx) ** 0.5
        out.append(f"\\node[circle,draw={color(d)},fill={color(d)}!12,line width=0.6pt,inner sep=0.5pt,"
                   f"minimum size={r*0.9:.2f}cm] ({ids[d]}) at ({(x-min(xs))*sx-5.5:.2f},{(y-min(ys))*sy-3.3:.2f}) "
                   f"{{\\texttt{{{lab(d)}}}}};")
    for a, b in G.edges():
        out.append(f"\\draw[gray,opacity=0.45,line width=0.4pt] ({ids[a]}) -- ({ids[b]});")
    out.append(r"\end{tikzpicture}")
    out.append(r"\caption{\textbf{Operator graph $G_O$ of " + FAMILY + r".} Nodes are operators (the "
               + str(len(top)) + r" with highest support), sized by frequency and coloured by change type "
               r"(\textcolor{NavyBlue}{voicing}, \textcolor{BurntOrange}{fricativization}, "
               r"\textcolor{ForestGreen}{palatalization/height}, \textcolor{Sepia}{place}, "
               r"\textcolor{Purple}{prenasalization}). An edge joins $u,v$ when their composition $u\oplus v$ is "
               r"itself an operator of the repertoire --- so this is the graph of \emph{additive closure}. "
               r"Dense connectivity is the visual face of the composition index $C(O)$.}")
    out.append(r"\end{figure}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
