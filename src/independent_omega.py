#!/usr/bin/env python3
"""FASE 1 · Oportunidad INDEPENDIENTE del alineador (revisión §3.3/§9: circularidad de Ω_D).

Ω_D (usado en universes/nulls) se construye desde NUESTRO alineamiento NW, así que ρ_opp y C_Ω son en parte
"medir el alineador contra sí mismo". Aquí construimos una oportunidad **independiente del alineamiento**:
Ω_bag = { Δ(a,b) : a,b consonantes que CO-OCURREN en formas del mismo concepto } — bag-of-segments por concepto,
sin usar NW ni cognacía. Comparamos tres denominadores para la ocupación y para la composición condicionada:
  · ρ_alg (span)  · ρ_seg (inventario U_S)  · ρ_opp (alineador Ω_D)  · ρ_bag (INDEPENDIENTE Ω_bag)
Si ρ_bag y C_bag siguen altos, la densidad/estructura no son artefacto del alineador.

Necesita corpora (forms.csv). Uso: TF_FAMILY="Indo-European" python3 src/independent_omega.py
"""
import os, csv, sqlite3, itertools
from collections import defaultdict
import panphon

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.abspath(os.path.join(HERE, "..", "data", "lexicon", "lexibank"))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MINEDGE = 30
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


def span_tester(O):
    used = [r for r in PRIM if any(r in d for d in O)]
    idx = {r: i for i, r in enumerate(used)}
    basis = []
    for d in O:
        v = sum(1 << idx[r] for r in d if r in idx)
        for b in basis: v = min(v, v ^ b)
        if v: basis.append(v); basis.sort(reverse=True)
    def in_span(d):
        if any(r not in idx for r in d): return False
        v = sum(1 << idx[r] for r in d)
        for b in basis: v = min(v, v ^ b)
        return v == 0
    return len(basis), in_span


def cofrac(O, target):
    s = set(O); n = len(O); num = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (O[i] ^ O[j]) in target: num += 1
    return num


def main():
    # O y Ω_D (alineador) desde transf.db; S para U_S
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    O, Omega_align, S = set(), set(), set()
    for a, b, c in rows:
        if is_cons(a): S.add(a)
        if is_cons(b): S.add(b)
        if a == b or not (is_cons(a) and is_cons(b)): continue
        d = delta(a, b)
        if not d: continue
        Omega_align.add(d)
        if c >= MINEDGE: O.add(d)
    O = list(O)
    U = {d for a, b in itertools.combinations(sorted(S), 2) if (d := delta(a, b))}

    # Ω_bag INDEPENDIENTE: consonantes co-presentes por concepto (sin alineamiento)
    lang_fam = {r["ID"]: (r.get("Family") or "") for r in csv.DictReader(open(f"{LEX}/languages.csv", encoding="utf-8"))}
    cons_by_concept = defaultdict(set)
    for row in csv.DictReader(open(f"{LEX}/forms.csv", encoding="utf-8")):
        if lang_fam.get(row["Language_ID"]) != FAMILY: continue
        for s in (row.get("Segments") or "").split():
            if is_cons(s): cons_by_concept[row["Parameter_ID"]].add(s)
    Omega_bag = set()
    for cset in cons_by_concept.values():
        for a, b in itertools.combinations(sorted(cset), 2):
            d = delta(a, b)
            if d: Omega_bag.add(d)

    r, in_span = span_tester(O)
    span = (1 << r) - 1
    U_in = {d for d in U if in_span(d)}
    Om_in = {d for d in Omega_align if in_span(d)}
    Bag_in = {d for d in Omega_bag if in_span(d)}
    Oset = set(O)

    print(f"\n=== FASE 1 · Oportunidad independiente · {FAMILY} ===")
    print(f"|O|={len(O)}  |Ω_align|={len(Omega_align)}  |Ω_bag(indep)|={len(Omega_bag)}  |U_S|={len(U)}  |span|={span}")
    print(f"\nOCUPACIÓN (|O| / universo ∩ span):")
    print(f"  ρ_alg (span)          = {len(O)/span:.3f}")
    print(f"  ρ_seg (inventario U_S) = {len(O)/max(1,len(U_in)):.3f}")
    print(f"  ρ_opp (alineador Ω_D)  = {len(O)/max(1,len(Om_in)):.3f}   ← posiblemente circular")
    print(f"  ρ_bag (INDEPENDIENTE)  = {len(O)/max(1,len(Bag_in)):.3f}   ← sin alineador")
    numO = cofrac(O, Oset)
    den_bag = cofrac(O, Bag_in); den_opp = cofrac(O, Om_in)
    print(f"\nCOMPOSICIÓN condicionada (de las composiciones que caen en el universo, cuántas en O):")
    print(f"  C_Ω  (alineador)  = {numO}/{den_opp} = {numO/max(1,den_opp):.3f}")
    print(f"  C_bag (INDEPEND.) = {numO}/{den_bag} = {numO/max(1,den_bag):.3f}")
    print(f"\nLectura: si ρ_bag y C_bag (denominador SIN alineador) siguen siendo sustanciales, la densidad y la")
    print("clausura composicional NO son artefacto de medir el alineador contra sí mismo.")


if __name__ == "__main__":
    main()
