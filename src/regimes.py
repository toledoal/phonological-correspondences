#!/usr/bin/env python3
"""V4-8 · Cuatro regímenes de corpus + préstamos (revisión colaborativa §7; idea-marco 2).

En vez de tratar el corpus conceptual como "peligroso", lo convertimos en CONTROL. Sobre IE-CoR (cognación
experta) comparamos la estructura M(·) de cuatro regímenes, para separar de dónde viene la estructura:

  D_G  cognación experta        → estructura ligada a continuidad histórica aceptada
  D_L  cognación LexStat        → estructura recuperable automáticamente
  D_C  mismo concepto sin cognacía → estructura formal ligada a equivalencia conceptual
  D_R  conceptos PERMUTADOS     → estructura por inventario/frecuencia sola (artefacto)

Para cada régimen medimos el 'fingerprint' estructural: |O|, C(O), τ, κ. Lo que CAE de D_G/D_C a D_R es señal
genealógica/semántica; lo que PERMANECE en D_R es artefacto de inventario.

PRÉSTAMOS (idea-marco 2): no como anotación sino según MUEVEN o no el sistema. Con is_loan de IE-CoR comparamos
el repertorio HEREDADO (sin préstamos) vs CON préstamos: ¿los préstamos añaden operadores nuevos (mueven el
sistema) o caen dentro de O (no lo mueven)?

Uso:  python3 src/regimes.py   (env TF_MAXLANG def 30)
"""
import logging; logging.disable(logging.INFO)
import os, json, random
from collections import defaultdict, Counter
import panphon
from lingpy import LexStat

HERE = os.path.dirname(os.path.abspath(__file__))
IEC = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "iecor"))
MAXLANG = int(os.environ.get("TF_MAXLANG", "30"))
MINSUP = 8
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
    raw = Counter()
    for forms in classes:
        for x in range(len(forms)):
            for y in range(x+1, len(forms)):
                if forms[x][0] == forms[y][0]: continue
                for a, b in align(forms[x][1], forms[y][1]):
                    if a != b and is_cons(a) and is_cons(b):
                        d = delta(a, b)
                        if d: raw[d] += 1
    return {d for d, c in raw.items() if c >= MINSUP}, raw


def cofO(O):
    O = list(O); s = set(O); n = len(O); real = 0
    for i in range(n):
        for j in range(i+1, n):
            if (O[i] ^ O[j]) in s: real += 1
    return real / (n*(n-1)//2) if n > 1 else 0.0


def tau(O):
    s = set(O); n = len(O)
    return sum(1 for u in O for v in O if (u ^ v) in s)/(n*n) if n else 0.0


def kappa(O):
    O = list(O)
    return len({u ^ v for u in O for v in O})/len(O) if O else 0.0


def fp(name, O):
    print(f"  {name:26} |O|={len(O):3}  C(O)={cofO(O):.3f}  τ={tau(O):.3f}  κ={kappa(O):.2f}")


def main():
    forms = json.load(open(f"{IEC}/forms.json", encoding="utf-8"))
    cs = json.load(open(f"{IEC}/cognate_sets.json", encoding="utf-8"))
    form_gold = {}
    for c in cs:
        for m in c["members"]:
            form_gold[m["form_id"]] = c["id"]

    per_lang = defaultdict(list); fmeta = {}
    for f in forms:
        segs = f.get("segments") or []
        if len(segs) < 2 or not f.get("concept_id"): continue
        per_lang[f["language_id"]].append(f["id"])
        fmeta[f["id"]] = (f["language_id"], f["concept_id"], segs, bool(f.get("is_loan")))
    langs = sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    fids = [fid for l in langs for fid in per_lang[l]]

    # D_G: clases de cognado experto
    gold = defaultdict(list)
    for fid in fids:
        g = form_gold.get(fid)
        if g: gold[g].append((fmeta[fid][0], fmeta[fid][2]))
    D_G = [v for v in gold.values() if len(v) >= 2]

    # D_C: mismo concepto (sin cognacía)
    conc = defaultdict(list)
    for fid in fids:
        conc[fmeta[fid][1]].append((fmeta[fid][0], fmeta[fid][2]))
    D_C = [v for v in conc.values() if len(v) >= 2]

    # D_R: conceptos permutados (rompe forma↔concepto → artefacto)
    rng = random.Random(2024)
    cids = [fmeta[fid][1] for fid in fids]; rng.shuffle(cids)
    permc = defaultdict(list)
    for fid, c in zip(fids, cids):
        permc[c].append((fmeta[fid][0], fmeta[fid][2]))
    D_R = [v for v in permc.values() if len(v) >= 2]

    # D_L: LexStat
    tsv = os.path.join(HERE, "..", "data", "db", "_reg.tsv")
    with open(tsv, "w", encoding="utf-8") as fh:
        fh.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1; idmap = {}
        for fid in fids:
            l, c, segs, _ = fmeta[fid]
            fh.write(f"{i}\t{l}\t{c}\t{' '.join(segs)}\n"); idmap[i] = fid; i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")
    lcl = defaultdict(list)
    for k in lex:
        lcl[(lex[k, "concept"], lex[k, "cogid"])].append((lex[k, "doculect"], lex[k, "tokens"]))
    D_L = [v for v in lcl.values() if len(v) >= 2]

    O_G, _ = ops_from(D_G); O_L, _ = ops_from(D_L); O_C, _ = ops_from(D_C); O_R, _ = ops_from(D_R)
    print(f"\n=== V4-8 · Cuatro regímenes de corpus · IE-CoR ({len(langs)} lenguas) ===")
    fp("D_G cognado experto", O_G)
    fp("D_L LexStat", O_L)
    fp("D_C concepto (sin cognacía)", O_C)
    fp("D_R concepto PERMUTADO", O_R)
    print(f"\n  Δ estructura (lo que CAE de D_C a D_R = señal semántico-formal, no artefacto de inventario):")
    print(f"    |O|: {len(O_C)}→{len(O_R)}   C(O): {cofO(O_C):.3f}→{cofO(O_R):.3f}   τ: {tau(O_C):.3f}→{tau(O_R):.3f}")
    print(f"    operadores en D_R que NO están en D_G (artefacto puro): {len(O_R - O_G)}/{len(O_R)}")

    # PRÉSTAMOS: heredado (sin loans) vs con loans, dentro de las clases de cognado experto
    goldH = defaultdict(list); goldA = defaultdict(list)
    for fid in fids:
        g = form_gold.get(fid)
        if not g: continue
        l, c, segs, loan = fmeta[fid]
        goldA[g].append((l, segs))
        if not loan: goldH[g].append((l, segs))
    OA, _ = ops_from([v for v in goldA.values() if len(v) >= 2])
    OH, _ = ops_from([v for v in goldH.values() if len(v) >= 2])
    nloan = sum(1 for fid in fids if fmeta[fid][3])
    print(f"\n  PRÉSTAMOS (is_loan) — ¿mueven el sistema? ({nloan} formas préstamo de {len(fids)}):")
    fp("  heredado (sin préstamos)", OH)
    fp("  con préstamos", OA)
    added = OA - OH
    print(f"    operadores que los préstamos AÑADEN al repertorio: {len(added)}  "
          + (f"→ {' '.join('{'+'+'.join(sorted(d))+'}' for d in list(added)[:6])}" if added else "→ ninguno"))
    print(f"    lectura: si añaden ~0, los préstamos NO mueven el repertorio (caen en operadores ya presentes);")
    print("    si añaden varios, el contacto introduce transformaciones nuevas al sistema.")


if __name__ == "__main__":
    main()
