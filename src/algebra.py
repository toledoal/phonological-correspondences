#!/usr/bin/env python3
"""X4 · Álgebra de operadores DENTRO de un sistema — transformations (composición, XOR, cierre).

Cada operador = un DELTA de rasgos (qué rasgos primarios cambian entre dos segmentos que se corresponden).
Componer dos operadores a~b y b~c = la DIFERENCIA SIMÉTRICA (XOR) de sus deltas → grupo ABELIANO (cada operador
es su propio inverso). Sobre las correspondencias reconstrucción-libres de una familia medimos:

  1) LEY XOR (empírica): en tríos a~b~c donde las 3 correspondencias existen, ¿delta(a,c)=delta(a,b)⊕delta(b,c)?
     Las desviaciones = CADENAS (a≠b≠c todos distintos en un rasgo, p.ej. t~ts~s = corredor de cambio).
  2) GENERADORES ATÓMICOS: qué operadores de UN solo rasgo usa el sistema (la "tabla periódica"); los compuestos
     ({voi+cor}) como XOR de átomos.
  3) CIERRE por composición: para caminos a~b~c, ¿la composición predicha a~c también es un operador observado
     del sistema? (tasa de cierre = ¿el conjunto de operadores es algebraicamente cerrado?).

Uso:  TF_FAMILY="Indo-European" python3 src/algebra.py
"""
import os, sqlite3, random
from collections import Counter, defaultdict
import panphon

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
PRIM = ["cont", "voi", "nas", "ant", "cor", "lab", "back", "round", "strid", "hi", "lo", "son"]
MINEDGE = 30
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


def delta(a, b):
    fa, fb = feat(a), feat(b)
    if fa is None or fb is None:
        return None
    return frozenset(k for k in PRIM if fa.get(k, 0) != fb.get(k, 0))


def fmt(d):
    return "{" + "+".join(sorted(d)) + "}" if d else "∅"


def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()

    edge = {}     # frozenset{a,b} -> (delta, count)
    adj = defaultdict(set)
    for a, b, c in rows:
        if a == b or c < MINEDGE or not (is_cons(a) and is_cons(b)):
            continue
        d = delta(a, b)
        if d is None or not (0 < len(d) <= 3):
            continue
        edge[frozenset((a, b))] = (d, c)
        adj[a].add(b); adj[b].add(a)

    def get(a, b):
        return edge.get(frozenset((a, b)))

    print(f"\n=== X4 · Álgebra de operadores en {FAMILY} ===")
    print(f"operadores (correspondencias con cambio de rasgo): {len(edge)}\n")

    # 1) LEY XOR sobre tríos completos.
    # ADVERTENCIA (revisión peer §2): con rasgos ESTRICTAMENTE binarios, delta(a,c)=delta(a,b)⊕delta(b,c) es una
    # IDENTIDAD (100% por construcción), no un hallazgo. panphon usa rasgos TERNARIOS (+1/0/-1). El XOR falla EXACTA
    # y solamente donde un rasgo toma 3 valores distintos entre a,b,c (dimensión graduada, no binaria). Por eso el
    # XOR-break no "descubre cadenas": DIAGNOSTICA qué dimensiones del sistema no son binarias (son graduadas).
    xor_ok = xor_no = 0
    graded = Counter()   # rasgo con 3 valores distintos entre a,b,c en un trío que rompe el XOR
    segs = list(adj)
    for a in segs:
        for b in adj[a]:
            if b <= a:
                continue
            for c in adj[b]:
                if c <= b or c == a:
                    continue
                if not get(a, c):
                    continue
                dab, dbc, dac = get(a, b)[0], get(b, c)[0], get(a, c)[0]
                if dac == (dab ^ dbc):
                    xor_ok += 1
                else:
                    xor_no += 1
                    fa, fb, fc = feat(a), feat(b), feat(c)
                    for r in PRIM:
                        if len({fa.get(r, 0), fb.get(r, 0), fc.get(r, 0)}) == 3:
                            graded[r] += 1
    tot = xor_ok + xor_no
    print("1) IDENTIDAD XOR (no es un hallazgo: es identidad sobre rasgos binarios):")
    print(f"   se cumple en {xor_ok}/{tot} tríos = {100*xor_ok/max(1,tot):.1f}%")
    print(f"   las {xor_no} desviaciones son TODAS dimensiones GRADUADAS (rasgo con 3 valores +1/0/-1 entre a,b,c):")
    if graded:
        print(f"   → dimensiones no-binarias del sistema: " + " · ".join(f"{r}:{n}" for r, n in graded.most_common(6)))
    print("   Lectura honesta: el álgebra binaria NO es una propiedad de las lenguas; el XOR-break LOCALIZA")
    print("   los ejes graduados (que deben modelarse con estados ordenados, no con bits).")

    # 2) generadores atómicos vs compuestos
    atoms = Counter(); comp = Counter()
    for d, c in edge.values():
        (atoms if len(d) == 1 else comp)[d] += c
    print(f"\n2) GENERADORES ATÓMICOS (operadores de UN rasgo — la 'tabla periódica' del sistema):")
    for d, c in atoms.most_common():
        print(f"   {fmt(d):14} n={c}")
    print(f"   compuestos (moléculas = XOR de átomos): {len(comp)} tipos; top: "
          + " · ".join(f"{fmt(d)}" for d, _ in comp.most_common(6)))
    # ¿los compuestos se generan por átomos presentes?
    atomset = set().union(*[set(d) for d in atoms]) if atoms else set()
    gen = sum(1 for d in comp if set(d) <= atomset)
    print(f"   {gen}/{len(comp)} compuestos usan solo rasgos que ya son átomos → "
          + ("el sistema está GENERADO por sus átomos" if gen == len(comp) else "hay rasgos solo-en-compuestos"))

    # 2b) RANGO F₂ (revisión peer §7): un operador monorrasgo es un vector base OBSERVADO, no un generador
    # independiente. El número de dimensiones REALES = rango sobre GF(2) de la matriz operadores×rasgos.
    deltas = [d for d, _ in edge.values()]
    used = [r for r in PRIM if any(r in d for d in deltas)]      # rasgos que cambian alguna vez
    idx = {r: i for i, r in enumerate(used)}
    matrix = []
    for d in deltas:
        row = 0
        for r in d:
            row |= (1 << idx[r])
        matrix.append(row)
    rank = gf2_rank(matrix)
    corank = len(used) - rank
    span = (1 << rank) - 1            # |V\{0}| = operadores generables no vacíos, V=span(O) sobre F₂
    ops = list(set(deltas))           # repertorio de operadores-TIPO (∅ excluido por construcción)
    occ = len(ops) / span if span else 0.0
    print(f"\n2b) RANGO / CORANGO / OCUPACIÓN (revisión peer §7, §terminología):")
    print(f"    rasgos codificados (que cambian alguna vez) = {len(used)}   rango F₂ = {rank}   corango = {corank}")
    print(f"    Aclaración: 'átomos' = operadores unitarios OBSERVADOS ({sum(1 for d in ops if len(d)==1)}); el rango")
    print(f"    se calcula sobre TODOS los rasgos presentes (incluidos los que solo aparecen en moléculas), por eso")
    print(f"    puede superar el nº de átomos. V = span_F₂(O) tiene {span} operadores no vacíos generables.")
    print(f"    OCUPACIÓN ρ = |O|/(|V|-1) = {len(ops)}/{span} = {occ:.4f}  (fracción del subespacio realmente usada)")
    if corank > 0:
        dep = gf2_col_dependency(deltas, used)
        if dep:
            r0, rest = dep[0], dep[1:]
            print(f"    DEPENDENCIA concreta (en ESTA muestra, patrón de activación entre operadores): "
                  f"columna '{r0}' = XOR({', '.join(rest)}) — no es reducción ontológica del rasgo, solo lineal.")

    # 3) ÍNDICE DE REALIZACIÓN COMPOSICIONAL (revisión peer §1.2 y §ronda3.1): NO es "cierre" (propiedad binaria).
    # Simplificado: como u≠v ⇒ u⊕v≠∅ en F₂, el denominador es exactamente C(|O|,2). ∅ no está en O.
    #   C(O) = |{ {u,v}⊆O : u⊕v ∈ O }| / C(|O|,2)
    opset = set(ops)
    real = 0
    for i in range(len(ops)):
        for j in range(i + 1, len(ops)):
            if (ops[i] ^ ops[j]) in opset:
                real += 1
    poss = len(ops) * (len(ops) - 1) // 2
    cobs = real / poss if poss else 0.0
    print(f"\n3) ÍNDICE DE REALIZACIÓN COMPOSICIONAL C(O) = |{{u,v}}:u⊕v∈O| / C(|O|,2):")
    print(f"   C(O) = {real}/{poss} = {cobs:.3f}")
    # modelo nulo condicionado (revisión peer §ronda3.2): repertorios nulos que PRESERVAN el tamaño de O y la
    # distribución de pesos de Hamming (tamaños de operador), muestreando cada operador como subconjunto aleatorio
    # de ese tamaño de los rasgos codificados ∝ su frecuencia marginal. Z = (C_obs - E[C_null]) / sd.
    z, mu, sd = cofO_null(ops, used, deltas, trials=400)
    print(f"   nulo condicionado (preserva |O| y pesos de Hamming): E[C]={mu:.3f} ± {sd:.3f}  →  Z = {z:+.2f}  "
          + ("(estructura por encima del azar)" if z > 2 else "(no distinguible del azar)" if abs(z) <= 2 else "(por DEBAJO del azar)"))

    # 4) MODELO NULO para "rasgos que nunca cambian solos" (revisión peer §8): la ausencia de un átomo NO prueba
    # dependencia. Comparamos co-ocurrencia observada de rasgos en operadores contra independencia marginal.
    natoms = sum(1 for d in ops if len(d) == 1)     # nº de operadores atómicos observados
    total_changes = sum(len(d) for d in ops)        # nº total de "slots" de rasgo que cambian
    print(f"\n4) DEPENDENCIA vs MODELO NULO ({natoms} operadores atómicos de {len(ops)} tipos):")
    print("   nulo: si los átomos se sortearan ∝ cuánto cambia cada rasgo, P(0 átomos = {r}) = (1-q_r)^A.")
    for r in used:
        alone = sum(1 for d in ops if d == frozenset({r}))
        if alone == 0:      # candidato a "nunca solo"
            q_r = sum(1 for d in ops if r in d) / max(1, total_changes)   # frecuencia relativa del rasgo
            p_none = (1 - q_r) ** natoms                                   # P(ningún átomo sea {r}) bajo el nulo
            partners = Counter()
            for d in ops:
                if r in d and len(d) > 1:
                    partners.update(d - {r})
            top = " ".join(f"{p}" for p, _ in partners.most_common(3))
            sig = "SIGNIFICATIVO" if p_none < 0.05 else "no sign."
            print(f"   {r:6} nunca solo · p(nulo)={p_none:.3f} [{sig}] · siempre con: {top or '—'}")
    print(f"\nLectura (revisada): el espacio COMPLETO de deltas binarios es un espacio vectorial sobre F₂; el repertorio")
    print(f"observado de {FAMILY} es un SUBCONJUNTO (no cerrado, C(O) medido arriba) de rango F₂ acotado. La identidad")
    print("XOR es de la representación; lo empírico son rango, densidad de realización y qué ejes son graduados.")


def gf2_rank(rows):
    """rango sobre GF(2) de una matriz dada como lista de enteros (filas como bitmasks)."""
    rows = [r for r in rows if r]
    rank = 0
    while rows:
        pivot = rows.pop()
        if not pivot:
            continue
        rank += 1
        low = pivot & -pivot           # bit más bajo como pivote
        rows = [(r ^ pivot) if (r & low) else r for r in rows]
    return rank


def gf2_col_dependency(deltas, used):
    """Halla una dependencia lineal (sobre GF2) entre las COLUMNAS-rasgo de la matriz operadores×rasgos.
    Columna r = qué operadores-tipo contienen r. Devuelve [r0, r1, ...] tal que col(r0)=XOR(col(r1..)), o None."""
    ops = list(set(deltas))
    cols = {r: sum((1 << i) for i, o in enumerate(ops) if r in o) for r in used}
    basis = {}   # bit-pivote -> (mask, conjunto de rasgos que lo generan)
    for r in used:
        cur, combo = cols[r], {r}
        while cur:
            low = cur & -cur
            if low in basis:
                bmask, bcombo = basis[low]
                cur ^= bmask; combo ^= bcombo
            else:
                break
        if cur:
            basis[cur & -cur] = (cur, combo)
        elif combo:
            return sorted(combo)     # combo XOR = 0  →  col(combo[0]) = XOR(resto)
    return None


def _cofO(ops):
    s = set(ops); n = len(ops); real = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (ops[i] ^ ops[j]) in s:
                real += 1
    return real / (n * (n - 1) // 2) if n > 1 else 0.0


def cofO_null(ops, used, deltas, trials=400):
    """Nulo condicionado de C(O): preserva |O| y la distribución de pesos de Hamming (tamaños), muestreando cada
    operador como subconjunto aleatorio de ese tamaño ∝ frecuencia marginal del rasgo. → (Z, media, sd)."""
    random.seed(42)
    sizes = [len(o) for o in ops]
    w = {r: sum(1 for o in ops if r in o) for r in used}
    feats = list(used); weights = [w[r] for r in feats]

    def draw(sz):
        chosen, pool, pw = set(), feats[:], weights[:]
        for _ in range(sz):
            t = sum(pw)
            x = random.random() * t
            k = 0
            while x > pw[k]:
                x -= pw[k]; k += 1
            chosen.add(pool[k]); del pool[k]; del pw[k]
        return frozenset(chosen)

    vals = []
    for _ in range(trials):
        seen = set()
        for sz in sizes:
            for _try in range(20):
                o = draw(sz)
                if o not in seen:
                    seen.add(o); break
        vals.append(_cofO(list(seen)))
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5
    cobs = _cofO(ops)
    return ((cobs - mu) / sd if sd else 0.0), mu, sd


if __name__ == "__main__":
    main()
