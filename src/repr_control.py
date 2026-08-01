#!/usr/bin/env python3
"""V4-6 · Control de estructura inducida por la REPRESENTACIÓN (revisión colaborativa §3.5, §3.6).

Una dependencia lineal en el repertorio observado O_L (p.ej. AN: col `ant` = XOR(`cor`,`lab`)) puede ser un
patrón del SISTEMA o una propiedad de la ONTOLOGÍA de rasgos / del inventario segmental. Para distinguirlo
comparamos O_L contra el UNIVERSO REALIZABLE U_S = { Δ(a,b) : a,b ∈ S }, donde S es el inventario de segmentos
consonánticos que la familia realmente usa. Si el rango y las dependencias de O_L coinciden con los de U_S, la
estructura es inducida por la representación; si O_L tiene MENOS rango / dependencias EXTRA, eso sí es del sistema.

Uso:  TF_FAMILY="Austronesian" python3 src/repr_control.py
"""
import os, sqlite3, itertools
import panphon
from algebra import gf2_rank, gf2_col_dependency

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Austronesian")
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


def rank_and_deps(op_list, used):
    idx = {r: i for i, r in enumerate(used)}
    mat = [sum(1 << idx[r] for r in d) for d in op_list]
    rank = gf2_rank(mat)
    # todas las dependencias de columnas (iterando: quita una columna hallada y repite)
    deps, remaining = [], list(used)
    while True:
        dep = gf2_col_dependency(op_list, remaining)
        if not dep:
            break
        deps.append(dep)
        remaining = [r for r in remaining if r != dep[0]]   # elimina la col dependiente y busca más
    return rank, deps


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()

    # O_L: operadores observados de la familia (consonánticos, soporte ≥30, delta 1..3)
    O = set()
    S = set()
    for a, b, c in rows:
        if is_cons(a): S.add(a)
        if is_cons(b): S.add(b)
        if a != b and c >= 30 and is_cons(a) and is_cons(b):
            d = delta(a, b)
            if d: O.add(d)
    O = list(O)

    # U_S: universo realizable = todos los Δ(a,b) entre segmentos consonánticos del inventario de la familia
    U = set()
    Sl = sorted(S)
    for a, b in itertools.combinations(Sl, 2):
        d = delta(a, b)
        if d: U.add(d)
    U = list(U)

    usedO = [r for r in PRIM if any(r in d for d in O)]
    usedU = [r for r in PRIM if any(r in d for d in U)]
    rO, depsO = rank_and_deps(O, usedO)
    rU, depsU = rank_and_deps(U, usedU)

    print(f"\n=== V4-6 · Control de representación · {FAMILY} ===")
    print(f"inventario segmental |S| = {len(S)} consonantes")
    print(f"repertorio observado  |O| = {len(O)} operadores · rasgos codif {len(usedO)} · rango {rO} · corango {len(usedO)-rO}")
    print(f"universo realizable   |U_S| = {len(U)} operadores · rasgos codif {len(usedU)} · rango {rU} · corango {len(usedU)-rU}")

    def fmtdeps(deps):
        return "  ·  ".join(f"{d[0]}=XOR({','.join(d[1:])})" for d in deps) or "(ninguna)"
    print(f"\ndependencias en O_L : {fmtdeps(depsO)}")
    print(f"dependencias en U_S : {fmtdeps(depsU)}")

    setO = {frozenset(d) for d in depsO}
    setU = {frozenset(d) for d in depsU}
    inherited = setO & setU
    system = setO - setU
    print(f"\nVEREDICTO:")
    if not depsO:
        print("  O_L no tiene dependencias (rango pleno): nada que atribuir.")
    else:
        if inherited:
            print(f"  {len(inherited)} dependencia(s) de O_L YA están en U_S → INDUCIDAS por la representación/inventario,")
            print(f"     no son un patrón del sistema: {', '.join('XOR('+ '+'.join(sorted(s)) +')' for s in inherited)}")
        if system:
            print(f"  {len(system)} dependencia(s) EXTRA de O_L (no en U_S) → propias del SISTEMA (uso selectivo).")
        if not system:
            print("  O_L no añade ninguna dependencia sobre U_S: su corango es enteramente representacional.")
    print("\nLectura: el corango del repertorio observado solo es 'del sistema' en la parte que EXCEDE al del")
    print("universo realizable U_S. Comparar rango(O_L) vs rango(U_S) separa representación de lenguas.")


if __name__ == "__main__":
    main()
