#!/usr/bin/env python3
"""X4 · Patrones matemáticos DENTRO de un sistema — transformations (enfoque intra-sistema).

Rumbo (PLAN §4d): la estructura matemática del cambio DENTRO de una familia, no universales ni comparación entre
sistemas. Sobre las correspondencias reconstrucción-libres de esa familia (LexStat, tabla lex_correspondence,
simétricas), extraemos:

  1) TABLA PERIÓDICA de operadores: distribución de los tipos de cambio por rasgos primarios (los "elementos").
  2) CLASES EMERGENTES: el grafo de correspondencias (nodos=segmentos, aristas=frecuencia a~b) se agrupa en
     comunidades = archifonemas descubiertos del PROPIO sistema (conecta con las clases OAS, pero emergentes).
  3) HUBS y estructura: qué segmentos participan en más cambios; conectividad; corredores preferentes.

Solo consonantes (las vocales son ruido de ablaut; conecta con el esqueleto consonántico).
Uso:  TF_FAMILY="Indo-European" python3 src/patterns.py
"""
import os, sqlite3, math
from collections import defaultdict, Counter
import panphon
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
MINEDGE = 30      # ignora correspondencias raras (ruido de alineamiento)
FT = panphon.FeatureTable()
_vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def is_cons(ph):
    f = feat(ph)
    return f is not None and f.get("syl", 0) != 1


def diffkey(a, b):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None:
        return None
    d = tuple(k for k in PRIM if fa.get(k, 0) != fb.get(k, 0))
    return d if 0 < len(d) <= 3 else None


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'",
                       (FAMILY,)).fetchall()
    con.close()

    # grafo de correspondencias consonánticas (simétrico)
    G = nx.Graph()
    optable = Counter()
    for a, b, c in rows:
        if a == b or c < MINEDGE or not (is_cons(a) and is_cons(b)):
            continue
        G.add_edge(a, b, weight=c)
        d = diffkey(a, b)
        if d:
            optable[d] += c

    print(f"\n=== Patrones matemáticos DENTRO de {FAMILY} (reconstrucción-libre) ===")
    print(f"grafo de cambio consonántico: {G.number_of_nodes()} segmentos · {G.number_of_edges()} correspondencias\n")

    # 1) tabla periódica de operadores
    tot = sum(optable.values()) or 1
    print("1) TABLA PERIÓDICA de operadores (tipo de cambio por rasgos · frecuencia):")
    for d, c in optable.most_common(12):
        key = "{" + "+".join(d) + "}"
        print(f"   {key:<26} {100*c/tot:4.1f}%  (n={c})")

    # 2) clases emergentes (comunidades del grafo)
    print("\n2) CLASES EMERGENTES (comunidades del grafo = archifonemas del propio sistema):")
    if G.number_of_edges():
        comms = greedy_modularity_communities(G, weight="weight")
        for i, cset in enumerate(sorted(comms, key=len, reverse=True)):
            if len(cset) < 2:
                continue
            # describir la clase por el rasgo más compartido
            print(f"   C{i}: {{{' '.join(sorted(cset))}}}")

    # 3) hubs (segmentos con más flujo de cambio) y estructura
    print("\n3) HUBS (segmentos con más 'flujo de cambio' = grado ponderado):")
    deg = sorted(G.degree(weight="weight"), key=lambda x: -x[1])[:8]
    print("   " + " · ".join(f"{s}({int(w)})" for s, w in deg))
    # corredores preferentes por frecuencia CRUDA (confundidos por frecuencia de segmento)
    edges = sorted(G.edges(data=True), key=lambda e: -e[2]["weight"])[:8]
    print("\n   CORREDORES por frecuencia cruda (¡confundidos por frecuencia de segmento!):")
    print("   " + " · ".join(f"{a}~{b}:{d['weight']}" for a, b, d in edges))

    # 4) corredores SISTEMÁTICOS por PMI (normaliza por frecuencia → los operadores reales del sistema)
    N = sum(d["weight"] for _, _, d in G.edges(data=True)) * 2
    flux = dict(G.degree(weight="weight"))
    pmi = []
    for a, b, d in G.edges(data=True):
        dk = diffkey(a, b)
        if d["weight"] < MINEDGE or dk is None:     # solo CAMBIOS de rasgo primario reales (no alófonos)
            continue
        val = math.log2(d["weight"] * N / (flux[a] * flux[b]))
        pmi.append((val, a, b, d["weight"], dk))
    pmi.sort(reverse=True)
    print("\n4) OPERADORES SISTEMÁTICOS (cambio de rasgo real + enriquecido por PMI sobre la frecuencia):")
    for val, a, b, w, dk in pmi[:14]:
        print(f"   {a}~{b:4} PMI={val:+.2f}  {'{'+'+'.join(dk)+'}':20} (n={w})")
    # agregar por TIPO de operador (rasgos): el operador más sistemático del sistema
    bytype = defaultdict(lambda: [0, 0.0])
    for val, a, b, w, dk in pmi:
        bytype[dk][0] += w; bytype[dk][1] += val * w
    print("\n   por TIPO de operador (peso × PMI medio — los ejes de cambio del sistema):")
    for dk, (w, sv) in sorted(bytype.items(), key=lambda x: -x[1][1])[:8]:
        print(f"   {'{'+'+'.join(dk)+'}':22} PMĪ={sv/w:+.2f}  n={w}")

    print(f"\nLectura: es la huella de cambio de ESTE sistema (sus operadores, sus clases, sus hubs), intra-sistema,")
    print("sin universales — la huella de cambio propia de este sistema (operadores, clases emergentes, hubs).")


if __name__ == "__main__":
    main()
