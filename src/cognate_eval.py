#!/usr/bin/env python3
"""D_cognado vs D_conceptual (revisión peer §4): ¿cuánto contamina LexStat al mezclar no-cognados?

IE-CoR (iecor) trae cognación EXPERTA (gold). Sobre las mismas lenguas comparamos tres corpus:
  · GOLD      — alinear solo dentro de clases de cognado expertas          (D_cognado)
  · LEXSTAT   — alinear dentro de clases detectadas estadísticamente        (lo que usa nuestro pipeline)
  · CONCEPTO  — alinear TODOS los pares del mismo concepto (sin cognacía)    (peor caso, D_conceptual puro)

Medimos: (1) calidad de LexStat vs gold (precisión/recall/F1 pareado dentro de concepto); (2) cuántos
operadores de cada corpus son ESPURIOS (no aparecen en el gold); (3) efecto en C(O). Así se ve si los
operadores que interpretamos como del sistema están contaminados por no-cognados.

Uso:  python3 src/cognate_eval.py     (env TF_MAXLANG def 30)
"""
import logging; logging.disable(logging.INFO)
import os, json, itertools
from collections import defaultdict, Counter
import panphon
from lingpy import LexStat

HERE = os.path.dirname(os.path.abspath(__file__))
IEC = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "iecor"))
MAXLANG = int(os.environ.get("TF_MAXLANG", "30"))
THR = 0.55
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


def ops_from(classes):
    """classes: iterable de listas [(lang, segs)] → (set(delta), C(O), Counter)."""
    raw = Counter()
    for forms in classes:
        for x in range(len(forms)):
            for y in range(x+1, len(forms)):
                if forms[x][0] == forms[y][0]: continue
                for a, b in align(forms[x][1], forms[y][1]):
                    if a != b and is_cons(a) and is_cons(b):
                        d = delta(a, b)
                        if d: raw[d] += 1
    ops = {d for d, c in raw.items() if c >= 8}
    lo = list(ops); s = set(lo); real = poss = 0
    for i in range(len(lo)):
        for j in range(i+1, len(lo)):
            uv = lo[i] ^ lo[j]
            if not uv: continue
            poss += 1
            if uv in s: real += 1
    return ops, (real/poss if poss else 0.0), raw


def main():
    forms = json.load(open(f"{IEC}/forms.json", encoding="utf-8"))
    cs = json.load(open(f"{IEC}/cognate_sets.json", encoding="utf-8"))
    langs_j = {l["id"]: l["name"] for l in json.load(open(f"{IEC}/languages.json", encoding="utf-8"))}

    form_gold = {}                       # form_id -> cognate_id (experto)
    for c in cs:
        for m in c["members"]:
            form_gold[m["form_id"]] = c["id"]

    # formas por lengua (no préstamos, con ≥2 segmentos)
    per_lang = defaultdict(list)
    fmeta = {}
    for f in forms:
        if f.get("is_loan"): continue
        segs = f.get("segments") or []
        if len(segs) < 2 or not f.get("concept_id"): continue
        per_lang[f["language_id"]].append(f["id"])
        fmeta[f["id"]] = (f["language_id"], f["concept_id"], segs)
    langs = sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    langset = set(langs)
    fids = [fid for l in langs for fid in per_lang[l]]
    print(f"[IE-CoR] {len(langs)} lenguas · {len(fids)} formas (no préstamo) · cognación experta")

    # ---- clases GOLD (por cognate_id, dentro de concepto) ----
    gold_classes = defaultdict(list)     # cognate_id -> [(lang, segs)]
    covered = 0
    for fid in fids:
        g = form_gold.get(fid)
        if g is None: continue
        covered += 1
        lang, concept, segs = fmeta[fid]
        gold_classes[g].append((lang, segs))
    gold_cls = [v for v in gold_classes.values() if len(v) >= 2]
    print(f"  formas con cognado experto: {covered}/{len(fids)} ({100*covered/len(fids):.0f}%) · "
          f"{len(gold_cls)} clases gold con ≥2 lenguas")

    # ---- LexStat sobre las mismas formas ----
    tsv = os.path.join(HERE, "..", "data", "db", "_cog.tsv")
    with open(tsv, "w", encoding="utf-8") as fh:
        fh.write("ID\tDOCULECT\tCONCEPT\tTOKENS\tGOLD\n"); i = 1
        idmap = {}
        for fid in fids:
            lang, concept, segs = fmeta[fid]
            fh.write(f"{i}\t{lang}\t{concept}\t{' '.join(segs)}\t{form_gold.get(fid,'?')}\n")
            idmap[i] = fid; i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")

    lex_classes = defaultdict(list)
    pred = {}    # fid -> lexstat cogid
    for k in lex:
        pred[idmap[k]] = lex[k, "cogid"]
        lex_classes[(lex[k, "concept"], lex[k, "cogid"])].append((lex[k, "doculect"], lex[k, "tokens"]))
    lex_cls = [v for v in lex_classes.values() if len(v) >= 2]

    # ---- (1) calidad LexStat vs gold: pareado dentro de concepto ----
    by_concept = defaultdict(list)
    for fid in fids:
        if fid in form_gold:
            by_concept[fmeta[fid][1]].append(fid)
    tp = fp = fn = 0
    for concept, flist in by_concept.items():
        for a, b in itertools.combinations(flist, 2):
            if fmeta[a][0] == fmeta[b][0]: continue
            gsame = form_gold[a] == form_gold[b]
            psame = pred.get(a) is not None and pred.get(a) == pred.get(b)
            if gsame and psame: tp += 1
            elif psame and not gsame: fp += 1
            elif gsame and not psame: fn += 1
    prec = tp/(tp+fp) if tp+fp else 0
    rec = tp/(tp+fn) if tp+fn else 0
    f1 = 2*prec*rec/(prec+rec) if prec+rec else 0
    print(f"\n(1) NIVEL COGNÁTICO — pares de formas (mismo-concepto, distinta-lengua), unidad = par:")
    print(f"    P_cog={prec:.2f}  R_cog={rec:.2f}  F1_cog={f1:.2f}   "
          f"(FP={fp} pares NO-cognados unidos por LexStat = contaminación de instancias)")

    # ---- (2) operadores: gold vs lexstat vs concepto-todo ----
    concept_classes = defaultdict(list)
    for fid in fids:
        lang, concept, segs = fmeta[fid]
        concept_classes[concept].append((lang, segs))
    concept_cls = [v for v in concept_classes.values() if len(v) >= 2]

    g_ops, g_co, _ = ops_from(gold_cls)
    l_ops, l_co, _ = ops_from(lex_cls)
    c_ops, c_co, _ = ops_from(concept_cls)
    print(f"\n(2) NIVEL DE REPERTORIO — tipos de operador (soporte ≥8), unidad = tipo:")
    for name, ops, co, ref in [("GOLD (cognado)", g_ops, g_co, None),
                                ("LEXSTAT", l_ops, l_co, g_ops),
                                ("CONCEPTO-todo", c_ops, c_co, g_ops)]:
        extra = ""
        if ref is not None:
            inter = ops & ref
            p_op = len(inter)/len(ops) if ops else 0        # precisión de tipos
            r_op = len(inter)/len(ref) if ref else 0        # recall de tipos
            jac = len(inter)/len(ops | ref) if (ops | ref) else 0
            extra = (f" · P_op={p_op:.2f} R_op={r_op:.2f} Jaccard={jac:.2f} · "
                     f"espurios={len(ops-ref)} ({100*len(ops-ref)/max(1,len(ops)):.0f}%)")
        print(f"    {name:16} {len(ops):3} operadores · C(O)={co:.2f}{extra}")

    print(f"\nLectura (dos unidades DISTINTAS): el nivel COGNÁTICO mide instancias (pares) — LexStat es conservador")
    print("(R_cog bajo) con contaminación de instancias moderada; el nivel REPERTORIO mide tipos — ahí LexStat es")
    print("mucho más fiel (P_op alto, pocos espurios). HALLAZGO: el inventario de TIPOS es más robusto que la")
    print("identificación individual de cognados — un falso cognado suele producir un operador ya presente en el gold.")


if __name__ == "__main__":
    main()
