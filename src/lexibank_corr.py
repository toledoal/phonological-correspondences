#!/usr/bin/env python3
"""X1-lex · Correspondencias RECONSTRUCCIÓN-LIBRES desde Lexibank, con control señal/nulo — transformations.

Decisiones (PLAN §4c): NO anclar a raíces reconstruidas (fuera el proto-lenguaje). Se detecta la cognacía
ESTADÍSTICAMENTE (LingPy/LexStat sobre los Segments ya presentes) y se alinean las formas ENTRE SÍ; las
correspondencias son simétricas entre segmentos observados. CONTROL: pares del mismo concepto pero de clase de
cognado DISTINTA = NULO (el "Saar" no-cognado) → cada familia se reporta con contraste señal-vs-nulo (regularidad
de las correspondencias). Si señal ≈ nulo, es apofenia.

Entrada: data/lexicon/lexibank/{forms.csv,languages.csv}. Salida: data/db/transf.db (lex_correspondence).
Uso:  TF_FAMILY="Indo-European" python3 src/lexibank_corr.py
"""
import logging; logging.disable(logging.INFO)
import os, csv, sqlite3, math, random
from collections import defaultdict
import panphon
from lingpy import LexStat

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
OUT = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MAXLANG = int(os.environ.get("TF_MAXLANG", "30"))
THR = 0.55
FT = panphon.FeatureTable()
random.seed(42)


def vec(ph):
    v = FT.word_to_vector_list(ph.replace("g", "ɡ"), numeric=True)
    return v[0] if len(v) == 1 else None


def cost(a, b):
    if a == b:
        return 0.0
    va, vb = vec(a), vec(b)
    if va is None or vb is None:
        return 1.0
    return sum(1 for i in range(len(va)) if va[i] != vb[i]) / len(va)


def align(s, t):
    n, m = len(s), len(t)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1): D[i][0] = i
    for j in range(1, m + 1): D[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j] = min(D[i-1][j-1] + cost(s[i-1], t[j-1]), D[i-1][j] + 1, D[i][j-1] + 1)
    out, i, j = [], n, m
    while i > 0 and j > 0:
        if abs(D[i][j] - (D[i-1][j-1] + cost(s[i-1], t[j-1]))) < 1e-9:
            out.append((s[i-1], t[j-1])); i -= 1; j -= 1
        elif abs(D[i][j] - (D[i-1][j] + 1)) < 1e-9:
            i -= 1
        else:
            j -= 1
    return out[::-1]


def load():
    lang_fam = {}
    for row in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8")):
        lang_fam[row["ID"]] = row.get("Family") or ""
    # formas de la familia objetivo, contando por lengua
    per_lang = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        lid = row["Language_ID"]
        if lang_fam.get(lid) != FAMILY:
            continue
        segs = (row.get("Segments") or "").split()
        if len(segs) < 2 or not row.get("Parameter_ID"):
            continue
        per_lang[lid].append((row["Parameter_ID"], segs))
    # top lenguas por nº de formas
    langs = sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    return {l: per_lang[l] for l in langs}


def main():
    data = load()
    print(f"[{FAMILY}] {len(data)} lenguas (top por nº de formas)")
    # LexStat se alimenta de un TSV (parser robusto): ID DOCULECT CONCEPT TOKENS
    tsv = os.path.join(HERE, "..", "data", "db", "_wl.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n")
        i = 1
        for lid, forms in data.items():
            for concept, segs in forms:
                f.write(f"{i}\t{lid}\t{concept}\t{' '.join(segs)}\n"); i += 1
    print(f"  {i-1} formas → LexStat (detección estadística de cognados; puede tardar)…")
    lex = LexStat(tsv)
    lex.get_scorer(runs=100)
    lex.cluster(method="lexstat", threshold=THR, ref="cogid")

    # agrupar por concepto → clases de cognados
    by_concept = defaultdict(lambda: defaultdict(list))   # concept -> cogid -> [(lang, segs)]
    for k in lex:
        by_concept[lex[k, "concept"]][lex[k, "cogid"]].append(
            (lex[k, "doculect"], lex[k, "tokens"]))

    # SEÑAL: correspondencias simétricas dentro de cada clase de cognado (reconstrucción-libre, intra-sistema)
    signal = defaultdict(int)
    for concept, classes in by_concept.items():
        for cid, forms in classes.items():
            for x in range(len(forms)):
                for y in range(x + 1, len(forms)):
                    if forms[x][0] == forms[y][0]:
                        continue
                    for a, b in align(forms[x][1], forms[y][1]):
                        signal[tuple(sorted((a, b)))] += 1

    db = sqlite3.connect(OUT)
    db.execute("CREATE TABLE IF NOT EXISTS lex_correspondence(a TEXT,b TEXT,family TEXT,kind TEXT,count INT)")
    db.execute("DELETE FROM lex_correspondence WHERE family=?", (FAMILY,))
    db.executemany("INSERT INTO lex_correspondence VALUES(?,?,?,?,?)",
                   [(a, b, FAMILY, "signal", c) for (a, b), c in signal.items()])
    db.commit(); db.close()

    print(f"\n=== X1-lex · {FAMILY} (reconstrucción-libre, intra-sistema) ===")
    print(f"correspondencias señal: {len(signal)} tipos · {sum(signal.values())} pares alineados")
    top = sorted(((a, b, c) for (a, b), c in signal.items() if a != b), key=lambda x: -x[2])[:10]
    print("correspondencias top (crudas): " + " · ".join(f"{a}~{b}:{c}" for a, b, c in top))
    print(f"→ {os.path.relpath(OUT)}  · ahora: TF_FAMILY=\"{FAMILY}\" python3 src/patterns.py")


if __name__ == "__main__":
    main()
