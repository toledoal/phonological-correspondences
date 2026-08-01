#!/usr/bin/env python3
"""V4-2/3 · Tres universos y tres ocupaciones (revisión colaborativa §3.2, §3.3).

La ocupación algebraica ρ_alg=|O|/(2^r−1) usa un denominador demasiado abstracto: 2^r−1 incluye vectores que
quizá no correspondan a ninguna diferencia entre dos segmentos válidos. Distinguimos tres universos anidados:

  O      ⊆  Ω_D          ⊆  U_S             ⊆  ⟨O⟩ (span) ⊆ F_2^n
  observado  oportunidad     realizable         generado

  · U_S = { Δ(a,b) : a,b ∈ S } — diferencias posibles entre segmentos del inventario S de la familia.
  · Ω_D = diferencias que EFECTIVAMENTE ocurren en posiciones alineadas del corpus (soporte ≥1, pre-umbral).
  · O   = repertorio observado (soporte ≥ MINEDGE).

Ocupaciones: ρ_alg=|O|/(2^r−1) · ρ_seg=|O|/|U_S∩⟨O⟩| · ρ_opp=|O|/|Ω_D∩⟨O⟩|.
Composicionalidad condicionada: C(O)=…/C(|O|,2)  vs  C_Ω(O)=|{u,v:u⊕v∈O}| / |{u,v:u⊕v∈Ω_D}|.
Cada número separa restricción ALGEBRAICA / de REPRESENTACIÓN / de las LENGUAS.

Uso:  TF_FAMILY="Indo-European" python3 src/universes.py
"""
import os, sqlite3, itertools
import panphon
from algebra import gf2_rank

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MINEDGE = 30
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


def load():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    O, Omega, S = set(), set(), set()
    for a, b, c in rows:
        if is_cons(a): S.add(a)
        if is_cons(b): S.add(b)
        if a == b or not (is_cons(a) and is_cons(b)):
            continue
        d = delta(a, b)
        if not d:
            continue
        Omega.add(d)                 # oportunidad: cualquier diferencia observada en posición alineada
        if c >= MINEDGE:
            O.add(d)                 # observado con soporte
    U = set()
    for a, b in itertools.combinations(sorted(S), 2):
        d = delta(a, b)
        if d: U.add(d)               # realizable: cualquier par del inventario
    return list(O), Omega, U, S


def span_membership(O):
    """función 'x ∈ ⟨O⟩': reducción gaussiana; devuelve (rank, tester)."""
    used = [r for r in PRIM if any(r in d for d in O)]
    idx = {r: i for i, r in enumerate(used)}
    basis = []
    def tomask(d): return sum(1 << idx[r] for r in d if r in idx)
    for d in O:
        v = tomask(d)
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v); basis.sort(reverse=True)
    def in_span(d):
        if any(r not in idx for r in d):     # usa un rasgo que O nunca toca → fuera del span
            return False
        v = tomask(d)
        for b in basis:
            v = min(v, v ^ b)
        return v == 0
    return len(basis), in_span


def cofrac(O, target):
    """|{u,v}⊂O : u⊕v ∈ target| / |{u,v}⊂O : u⊕v ∈ dom|  — dom se fija fuera."""
    s = set(O); n = len(O); num = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (O[i] ^ O[j]) in target:
                num += 1
    return num, n * (n - 1) // 2


def main():
    O, Omega, U, S = load()
    r, in_span = span_membership(O)
    span = (1 << r) - 1
    U_in = {d for d in U if in_span(d)}
    Om_in = {d for d in Omega if in_span(d)}
    Oset = set(O)

    print(f"\n=== V4-2/3 · Universos y ocupaciones · {FAMILY} ===")
    print(f"|S| (inventario consonántico) = {len(S)}")
    print(f"|O| (observado, soporte≥{MINEDGE}) = {len(O)}   ⊆   |Ω_D| (oportunidad) = {len(Omega)}   ⊆   "
          f"|U_S| (realizable) = {len(U)}   ⊆   |⟨O⟩−0| = {span}   (rango {r})")
    print(f"\nOCUPACIONES (qué fracción del universo ocupa O):")
    print(f"  ρ_alg = |O|/(2^r−1)      = {len(O)}/{span} = {len(O)/span:.4f}   (restricción ALGEBRAICA)")
    print(f"  ρ_seg = |O|/|U_S∩⟨O⟩|    = {len(O)}/{len(U_in)} = {len(O)/max(1,len(U_in)):.4f}   (+ REPRESENTACIÓN/inventario)")
    print(f"  ρ_opp = |O|/|Ω_D∩⟨O⟩|    = {len(O)}/{len(Om_in)} = {len(O)/max(1,len(Om_in)):.4f}   (+ oportunidad del CORPUS)")

    numO, den = cofrac(O, Oset)
    numOm, _ = cofrac(O, Om_in)
    numU, _ = cofrac(O, U_in)
    print(f"\nCOMPOSICIONALIDAD (¿la composición u⊕v cae en…?):")
    print(f"  C(O)     = {numO}/{den} = {numO/max(1,den):.3f}   (composición vuelve a O)")
    print(f"  C_Ω(O)   = {numO}/{numOm} = {numO/max(1,numOm):.3f}   (de las que caen en la OPORTUNIDAD, cuántas en O)")
    print(f"  C_U(O)   = {numO}/{numU} = {numO/max(1,numU):.3f}   (de las que caen en lo REALIZABLE, cuántas en O)")
    print(f"\nLectura: si ρ_opp ≫ ρ_alg, la 'escasez' es sobre todo ALGEBRAICA (el span es enorme); lo que las")
    print("lenguas realmente eligen se ve mejor en ρ_opp y C_Ω, medidos contra lo que el corpus hizo disponible.")


if __name__ == "__main__":
    main()
