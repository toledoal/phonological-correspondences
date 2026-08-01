#!/usr/bin/env python3
"""¿El "álgebra" de una familia es la SUPERPOSICIÓN de álgebras de rama? (revisión peer §6)

Para cada RAMA (subgrupo genealógico, vía Glottolog → src/branches.py) corre LexStat DENTRO de la rama, extrae
su conjunto de operadores (deltas de rasgo consonánticos) y lo compara con el de las demás ramas y con el
agregado familiar. Responde: (a) ¿las ramas hacen la MISMA álgebra (Jaccard alto = regularidad de familia) o
DISTINTAS (Jaccard bajo = superposición)? (b) ¿los operadores de la familia están presentes DENTRO de alguna
rama, o son artefactos de alinear ENTRE ramas? (c) ¿una rama mejor muestreada domina?

Uso:  TF_FAMILY="Indo-European" python3 src/branch_algebra.py
Env:  TF_BR_MINLANGS (min lenguas por rama, def 8) · TF_BR_MAXLANG (top lenguas/rama, def 12) · TF_BRANCH_MAXFRAC
"""
import logging; logging.disable(logging.INFO)
import os, csv, sqlite3, itertools, random
from collections import defaultdict, Counter
import panphon
from lingpy import LexStat
from branches import branch_map

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MINLANGS = int(os.environ.get("TF_BR_MINLANGS", "8"))
MAXLANG = int(os.environ.get("TF_BR_MAXLANG", "12"))
MINEDGE = int(os.environ.get("TF_BR_MINEDGE", "8"))
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


def cofO(ops):
    ops = list(ops); s = set(ops); real = poss = 0
    for i in range(len(ops)):
        for j in range(i+1, len(ops)):
            uv = ops[i] ^ ops[j]
            if not uv: continue
            poss += 1
            if uv in s: real += 1
    return real / poss if poss else 0.0


def operators_for(langset, fixed=None):
    """LexStat dentro de un conjunto de lenguas → Counter(delta→count) de operadores consonánticos.
    Si fixed es una lista de IDs, usa exactamente esas (para rarefacción); si no, toma las top MAXLANG."""
    per_lang = defaultdict(list)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        lid = row["Language_ID"]
        if lid not in langset: continue
        segs = (row.get("Segments") or "").split()
        if len(segs) >= 2 and row.get("Parameter_ID"):
            per_lang[lid].append((row["Parameter_ID"], segs))
    langs = list(fixed) if fixed else sorted(per_lang, key=lambda l: -len(per_lang[l]))[:MAXLANG]
    langs = [l for l in langs if l in per_lang]
    if len(langs) < 2: return Counter(), 0
    tsv = os.path.join(HERE, "..", "data", "db", "_br.tsv")
    with open(tsv, "w", encoding="utf-8") as f:
        f.write("ID\tDOCULECT\tCONCEPT\tTOKENS\n"); i = 1
        for l in langs:
            for concept, segs in per_lang[l]:
                f.write(f"{i}\t{l}\t{concept}\t{' '.join(segs)}\n"); i += 1
    lex = LexStat(tsv); lex.get_scorer(runs=100); lex.cluster(method="lexstat", threshold=THR, ref="cogid")
    by = defaultdict(lambda: defaultdict(list))
    for k in lex:
        by[lex[k, "concept"]][lex[k, "cogid"]].append((lex[k, "doculect"], lex[k, "tokens"]))
    raw = Counter()
    for concept, classes in by.items():
        for cid, forms in classes.items():
            for x in range(len(forms)):
                for y in range(x+1, len(forms)):
                    if forms[x][0] == forms[y][0]: continue
                    for a, b in align(forms[x][1], forms[y][1]):
                        if a != b and is_cons(a) and is_cons(b):
                            d = delta(a, b)
                            if d: raw[d] += 1
    return raw, len(langs)


def main():
    assign, counts, ok = branch_map(FAMILY)
    if not ok:
        print(f"[{FAMILY}] sin clasificación Glottolog (¿familia no en FAMILY_ROOT?)"); return
    branches = [b for b, n in counts.most_common() if n >= MINLANGS]
    langs_by_branch = defaultdict(set)
    for lid, b in assign.items():
        if b in branches: langs_by_branch[b].add(lid)

    print(f"\n=== ¿Superposición de ramas? · {FAMILY} ===")
    print(f"{len(assign)} lenguas clasificadas · {len(branches)} ramas con ≥{MINLANGS} lenguas · "
          f"top {MAXLANG} lenguas/rama, MINEDGE={MINEDGE}\n")

    br_ops = {}     # rama -> set(delta) con soporte ≥ MINEDGE
    br_raw = {}     # rama -> Counter(delta) crudo
    for b in branches:
        raw, nl = operators_for(langs_by_branch[b])
        ops = {d for d, c in raw.items() if c >= MINEDGE}
        br_ops[b] = ops; br_raw[b] = raw
        atoms = sorted((("{"+"+".join(sorted(d))+"}") for d in ops if len(d) == 1))
        print(f"● {b:34} {nl:2} lenguas · {len(ops):3} operadores · C(O)={cofO(ops):.2f} · "
              f"{len(atoms)} átomos: {' '.join(atoms)[:60]}")

    R = len(branches)

    def mean_jaccard(opsets):
        vals = [len(a & b) / len(a | b) for a, b in itertools.combinations(opsets, 2) if (a | b)]
        return (sum(vals) / len(vals), min(vals), max(vals)) if vals else (0.0, 0.0, 0.0)

    # (a) similitud entre ramas: ¿misma álgebra o distintas?
    jm, jlo, jhi = mean_jaccard([br_ops[b] for b in branches])
    print(f"\n(a) JACCARD entre conjuntos de operadores de rama (1=idéntica, 0=disjunta):")
    print(f"    Jaccard medio (no ponderado) = {jm:.2f}  (rango {jlo:.2f}–{jhi:.2f})")

    # (b) REPERTORIO DE FAMILIA como UNIÓN de ramas (revisión colab §3.1: un solo universo, sin mezclar).
    #     O_F := ∪_r O_r ; p(o) = fracción de ramas que contienen o ; H_k = # operadores en exactamente k ramas.
    O_F = set().union(*[br_ops[b] for b in branches]) if branches else set()
    inbranches = {o: sum(1 for b in branches if o in br_ops[b]) for o in O_F}
    H = Counter(inbranches.values())                       # H_k, suma = |O_F| por construcción
    assert sum(H.values()) == len(O_F)
    K_cap = sum(1 for o in O_F if inbranches[o] == R)       # núcleo estricto (en TODAS)
    K_half = sum(1 for o in O_F if inbranches[o] >= (R + 1) // 2)  # núcleo mayoritario (≥⌈R/2⌉)
    excl = H.get(1, 0)
    print(f"\n(b) FAMILIA como unión de {R} ramas · |O_F| = {len(O_F)} (Σ H_k = {sum(H.values())} ✓):")
    print("    H_k (operadores en exactamente k ramas): " + " · ".join(f"{k}:{H[k]}" for k in sorted(H, reverse=True)))
    print(f"    K∩ (en las {R} ramas) = {K_cap}  ·  K½ (en ≥⌈{R}/2⌉={ (R+1)//2 } ramas) = {K_half}  ·  exclusivos (1 rama) = {excl}")
    shared_atoms = sorted({("{"+"+".join(sorted(o))+"}") for o in O_F if len(o) == 1 and inbranches[o] == R})
    print(f"    átomos en TODAS las ramas: {' '.join(shared_atoms) or '—'}")

    # coherencia (universo SEPARADO, etiquetado): el run whole-family vs la unión de ramas
    con = sqlite3.connect(DB)
    frows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    fam_ops = set()
    for a, b, c in frows:
        if a != b and c >= 30 and is_cons(a) and is_cons(b):
            d = delta(a, b)
            if d: fam_ops.add(d)
    if fam_ops:
        print(f"    [coherencia, OTRO universo] operadores del run whole-family = {len(fam_ops)}; "
              f"de ellos en ≥1 rama: {100*len(fam_ops & O_F)/len(fam_ops):.0f}%")

    # (c) RAREFACCIÓN de Jaccard y núcleo (revisión colab §3.8): ¿son robustos al tamaño de muestra?
    if os.environ.get("TF_RAREFY"):
        n_min = min(min(len(langs_by_branch[b]) for b in branches), MAXLANG)
        Rr = int(os.environ.get("TF_RAREFY", "3"))
        random.seed(7)
        jms, khalfs = [], []
        for _ in range(Rr):
            rar = {}
            for b in branches:
                sub = random.sample(sorted(langs_by_branch[b]), n_min)
                raw, _ = operators_for(langs_by_branch[b], fixed=sub)
                rar[b] = {d for d, c in raw.items() if c >= MINEDGE}
            jms.append(mean_jaccard([rar[b] for b in branches])[0])
            Ofr = set().union(*rar.values())
            khalfs.append(sum(1 for o in Ofr if sum(1 for b in branches if o in rar[b]) >= (R+1)//2))
        mj = sum(jms)/len(jms); sj = (sum((x-mj)**2 for x in jms)/len(jms))**0.5
        mk = sum(khalfs)/len(khalfs)
        print(f"\n(c) RAREFACCIÓN a n={n_min} lenguas/rama ({Rr} sorteos):")
        print(f"    Jaccard medio bruto={jm:.2f} → rarefacto={mj:.2f}±{sj:.2f}   (robusto si ~igual)")
        print(f"    K½ bruto={K_half} → rarefacto={mk:.1f}")

    # (d) NULO de agrupamiento (revisión colab §3.8, §9): ¿las ramas GENEALÓGICAS comparten más/menos que
    #     agrupaciones ARBITRARIAS del mismo tamaño? Permutamos etiquetas de rama conservando tamaños.
    if os.environ.get("TF_NULLBRANCH"):
        B = int(os.environ.get("TF_NULLBRANCH", "3"))
        random.seed(11)
        alllangs = [l for b in branches for l in langs_by_branch[b]]
        sizes = [len(langs_by_branch[b]) for b in branches]
        nulls = []
        for _ in range(B):
            pool = alllangs[:]; random.shuffle(pool)
            groups, i = [], 0
            for s in sizes:
                groups.append(pool[i:i+s]); i += s
            gops = []
            for g in groups:
                raw, _ = operators_for(set(g), fixed=g[:MAXLANG])
                gops.append({d for d, c in raw.items() if c >= MINEDGE})
            nulls.append(mean_jaccard(gops)[0])
        mn = sum(nulls)/len(nulls); sn = (sum((x-mn)**2 for x in nulls)/len(nulls))**0.5
        z = (jm - mn)/sn if sn else 0.0
        print(f"\n(d) NULO de agrupamiento arbitrario ({B} permutaciones de etiqueta, mismos tamaños):")
        print(f"    Jaccard real={jm:.2f}  vs  pseudo-ramas={mn:.2f}±{sn:.2f}   Z={z:+.2f}  "
              + ("(las ramas reales se diferencian MÁS que el azar)" if z < -1.5
                 else "(comparten MÁS que el azar)" if z > 1.5 else "(no distinguible del azar)"))

    print(f"\nLectura: O_F = unión de ramas; núcleo K∩/K½ = regularidad compartida; exclusivos = extensiones de")
    print("rama. La suma Σ H_k = |O_F| evita el doble conteo de la v3. Jaccard/núcleo se validan por rarefacción")
    print("y contra un nulo de agrupamiento arbitrario.")


if __name__ == "__main__":
    main()
