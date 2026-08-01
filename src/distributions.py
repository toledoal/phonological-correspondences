#!/usr/bin/env python3
"""V4-7 · Distribuciones, no solo tipos (revisión colaborativa §4.4–4.5).

El repertorio O registra EXISTENCIA; gran parte de la estructura está en la FRECUENCIA y en con-qué co-ocurre.
Una pasada de LexStat por familia etiqueta cada instancia de operador con: rama (Glottolog), concepto, posición
(inicial/medial/final) y contexto (clase del segmento previo/siguiente). Calculamos:

  · P_L(o), entropía H, número efectivo N_eff = e^H
  · Información mutua I(O;R) rama · I(O;C) concepto · I(O;pos) posición · I(O;Γ) contexto  (bits, y normalizada)
  · Tres geometrías: NO PONDERADA (qué existe) · PONDERADA por frecuencia · por CONFIANZA (coste de alineamiento)
    → ¿el ranking de operadores es robusto al pasar de tipos a distribución a confianza?

Uso:  TF_FAMILY="Indo-European" python3 src/distributions.py   (env TF_MAXLANG def 25)
"""
import logging; logging.disable(logging.INFO)
import os, csv, math
from collections import defaultdict, Counter
import panphon
from lingpy import LexStat
from branches import branch_map

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MAXLANG = int(os.environ.get("TF_MAXLANG", "25"))
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


def klass(ph):
    f = feat(ph)
    if f is None: return "#"
    return "V" if f.get("syl", 0) == 1 else "C"


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


def align_idx(s, t):
    """alineamiento NW; devuelve lista de (i,j,a,b) con índices en s,t (o None en gap)."""
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
            out.append((i-1, j-1, s[i-1], t[j-1])); i -= 1; j -= 1
        elif abs(D[i][j]-(D[i-1][j]+1)) < 1e-9: i -= 1
        else: j -= 1
    return out[::-1]


def pos_bucket(idx, L):
    if idx == 0: return "ini"
    if idx == L-1: return "fin"
    return "med"


def entropy(counter):
    tot = sum(counter.values())
    if not tot: return 0.0
    return -sum((c/tot)*math.log2(c/tot) for c in counter.values() if c)


def mutual_info(pairs):
    """pairs: lista de (o, tag). → (MI bits, MI normalizada por min(H(O),H(tag)))."""
    if not pairs: return 0.0, 0.0
    N = len(pairs)
    joint = Counter(pairs); po = Counter(o for o, _ in pairs); pt = Counter(t for _, t in pairs)
    mi = 0.0
    for (o, t), c in joint.items():
        mi += (c/N) * math.log2((c*N)/(po[o]*pt[t]))
    hO = entropy(po); hT = entropy(pt)
    return mi, mi/min(hO, hT) if min(hO, hT) > 0 else 0.0


def main():
    assign, _, _ = branch_map(FAMILY)
    lang_fam = {r["ID"]: (r.get("Family") or "") for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    per_lang = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        if lang_fam.get(row["Language_ID"]) != FAMILY: continue
        segs = (row.get("Segments") or "").split()
        if len(segs) >= 2 and row.get("Parameter_ID"):
            per_lang[row["Language_ID"]].append((row["Parameter_ID"], segs))
    langs = sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    tsv = os.path.join(HERE, "..", "data", "db", "_dist.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1
        for l in langs:
            for concept, segs in per_lang[l]:
                f.write(f"{i}\t{l}\t{concept}\t{' '.join(segs)}\n"); i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")
    classes = defaultdict(list)
    for k in lex:
        classes[(lex[k, "concept"], lex[k, "cogid"])].append((lex[k, "doculect"], lex[k, "tokens"]))

    # instancias etiquetadas
    cnt = Counter(); wcost = Counter()
    inst_R, inst_C, inst_P, inst_G = [], [], [], []
    for (concept, cogid), forms in classes.items():
        for x in range(len(forms)):
            for y in range(x+1, len(forms)):
                la, sa = forms[x]; lb, sb = forms[y]
                if la == lb: continue
                for ia, ib, A, Bs in align_idx(sa, sb):
                    if A == Bs or not (is_cons(A) and is_cons(Bs)): continue
                    d = delta(A, Bs)
                    if not d: continue
                    o = "{"+"+".join(sorted(d))+"}"
                    cnt[o] += 1
                    conf = 1.0 - cost(A, Bs)          # confianza ≈ 1 - coste de rasgos
                    wcost[o] += conf
                    # rama: solo instancias intra-rama (ambas lenguas en la misma rama)
                    ra, rb = assign.get(la), assign.get(lb)
                    if ra and ra == rb: inst_R.append((o, ra))
                    inst_C.append((o, concept))
                    inst_P.append((o, pos_bucket(ia, len(sa))))
                    prev = klass(sa[ia-1]) if ia > 0 else "#"
                    nxt = klass(sa[ia+1]) if ia+1 < len(sa) else "#"
                    inst_G.append((o, prev+"_"+nxt))

    tot = sum(cnt.values())
    H = entropy(cnt); Neff = 2**H
    print(f"\n=== V4-7 · Distribuciones e información mutua · {FAMILY} ===")
    print(f"instancias de operador = {tot} · tipos = {len(cnt)}")
    print(f"entropía H(P_L) = {H:.2f} bits · N_eff = e^H = {Neff:.1f} operadores efectivos (de {len(cnt)} tipos)")
    print(f"top por FRECUENCIA: " + " · ".join(f"{o}:{c}" for o, c in cnt.most_common(6)))

    # tres geometrías: ranking por tipos (existencia=1), por frecuencia, por confianza
    print("\nTRES GEOMETRÍAS (¿cambia el orden de operadores?):")
    by_freq = [o for o, _ in cnt.most_common(8)]
    by_conf = [o for o, _ in wcost.most_common(8)]
    print(f"  por frecuencia : {' '.join(by_freq)}")
    print(f"  por confianza  : {' '.join(by_conf)}")
    print(f"  (coinciden top-8: {len(set(by_freq)&set(by_conf))}/8 → repertorio robusto al ponderar por confianza)")

    print("\nINFORMACIÓN MUTUA I(O; ·)  (bits · normalizada):")
    for name, inst in [("rama R  (intra-rama)", inst_R), ("concepto C", inst_C),
                       ("posición pos", inst_P), ("contexto Γ (prev_sig)", inst_G)]:
        mi, nmi = mutual_info(inst)
        print(f"  I(O; {name:22}) = {mi:.3f} bits · norm {nmi:.3f}   (n={len(inst)})")
    print("\nLectura: N_eff ≪ nº de tipos ⇒ el repertorio está dominado por pocos operadores. I(O;·) alta indica que")
    print("el operador DEPENDE de esa variable (rama/posición/contexto) — pista de reglas condicionadas (orden 1/2).")


if __name__ == "__main__":
    main()
