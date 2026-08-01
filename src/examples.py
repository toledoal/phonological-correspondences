#!/usr/bin/env python3
"""Ejemplos en PALABRAS REALES: conjuntos de cognados alineados con IPA y los operadores en acción.

Corre LexStat en una familia, toma clases de cognados grandes, muestra las formas (lengua: IPA) y los operadores
(cambios de rasgo) que aparecen entre pares de la clase. Imprime un fragmento Markdown para el documento.
Uso: TF_FAMILY="Indo-European" python3 src/examples.py
"""
import logging; logging.disable(logging.INFO)
import os, csv
from collections import defaultdict, Counter
import panphon
from lingpy import LexStat

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MAXLANG = 15
NSETS = int(os.environ.get("TF_NSETS", "4"))
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
FT = panphon.FeatureTable()
_vc = {}


def feat(ph):
    if ph not in _vc:
        v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
        _vc[ph] = dict(zip(FT.names, v[0])) if len(v) == 1 else None
    return _vc[ph]


def dset(a, b):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None: return None
    return frozenset(k for k in PRIM if fa.get(k, 0) != fb.get(k, 0))


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


def main():
    lang_fam = {r["ID"]: (r.get("Family") or "") for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    lang_name = {r["ID"]: r.get("Name") or r["ID"] for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    per_lang = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        if lang_fam.get(row["Language_ID"]) != FAMILY: continue
        segs = (row.get("Segments") or "").split()
        if len(segs) >= 2 and row.get("Parameter_ID"):
            per_lang[row["Language_ID"]].append((row["Parameter_ID"], segs))
    langs = sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    tsv = os.path.join(HERE, "..", "data", "db", "_ex.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1
        for l in langs:
            for concept, segs in per_lang[l]:
                f.write(f"{i}\t{l}\t{concept}\t{' '.join(segs)}\n"); i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=0.55, ref="cogid")

    classes = defaultdict(list)   # (concept,cogid) -> [(lang, segs)]
    for k in lex:
        classes[(lex[k, "concept"], lex[k, "cogid"])].append((lex[k, "doculect"], lex[k, "tokens"]))

    def tightness(items):   # coste medio de alineamiento por posición (bajo = cognados de verdad)
        cs = []
        for x in range(len(items)):
            for y in range(x + 1, len(items)):
                al = align(items[x][1], items[y][1])
                if al:
                    cs.append(sum(cost(a, b) for a, b in al) / len(al))
        return sum(cs) / len(cs) if cs else 1.0

    # conceptos de vocabulario básico HEREDADO (evita préstamos internacionales tipo 'bamboo/ocean';
    # ahí es donde los cambios de sonido regulares son visibles). Se puede pasar por TF_CONCEPTS.
    PREFER = os.environ.get("TF_CONCEPTS", "").split(",") if os.environ.get("TF_CONCEPTS") else [
        "three", "two", "tooth", "foot", "night", "new", "name", "nose", "star", "mother",
        "father", "fish", "heart", "ear", "eye", "fire", "hand", "knee", "dog", "seven"]
    # para cada concepto preferido, su clase de cognados MÁS grande (la serie heredada principal)
    cands = []
    for concept in PREFER:
        best = None
        for (c, cogid), forms in classes.items():
            if c != concept:
                continue
            uniq = {}
            for l, s in forms:
                uniq.setdefault(l, s)
            if len(uniq) >= 5 and (best is None or len(uniq) > len(best[1])):
                items = list(uniq.items())[:7]
                best = (concept, items, tightness(items))
        if best and best[2] < 0.45:       # cohesión laxa (los heredados divergen más que los préstamos)
            cands.append((best[2], best[0], best[1]))
    print(f"### Ejemplos en palabras reales — {FAMILY}\n")
    print(f"(vocabulario básico heredado; conjuntos de cognados de LexStat, mostrando los operadores en acción)\n")
    shown = 0
    for t, concept, items in cands:
        print(f"**'{concept}'** (conjunto de cognados):")
        print("| lengua | forma (IPA) |")
        print("|---|---|")
        for l, s in items:
            print(f"| {lang_name.get(l, l)} | /{''.join(s)}/ |")
        # operadores entre el primer par divergente
        ops = Counter()
        for x in range(len(items)):
            for y in range(x+1, len(items)):
                for a, b in align(items[x][1], items[y][1]):
                    if a != b:
                        d = dset(a, b)
                        if d and 0 < len(d) <= 3:
                            ops[(a, b, d)] += 1
        top = ops.most_common(5)
        print("\noperadores presentes: " + " · ".join(
            f"{a}~{b} {{{'+'.join(sorted(d))}}}" for (a, b, d), _ in top) + "\n")
        shown += 1
        if shown >= NSETS: break


if __name__ == "__main__":
    main()
