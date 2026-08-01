#!/usr/bin/env python3
"""V4-4 · Jerarquía de modelos nulos para C(O) (revisión colaborativa §3.4).

Un solo nulo no basta: hay que ver a QUÉ restricción sobrevive la composicionalidad observada. Anidamos:

  Nulo 0  tamaño + peso≤3   — |O| vectores aleatorios de peso 1..3 sobre los n rasgos.
  Nulo 1  pesos de Hamming  — preserva el multiconjunto de tamaños de operador.
  Nulo 2  marginales exactas — swap-MCMC: preserva sumas de fila (tamaños) Y de columna (frecuencia de rasgo).
  Nulo 3  rango / span      — |O| vectores del subespacio ⟨O⟩.
  Nulo 4  realizable U_S    — |O| vectores de U_S (diferencias entre segmentos del inventario).
  Nulo 5  oportunidad Ω_D   — |O| vectores de Ω_D (diferencias efectivamente disponibles en el corpus).

Para cada uno: E[C], sd, Z y p_MC=(1+#{C_null≥C_obs})/(B+1). Si C(O) sobrevive a los nulos 3–5, ya no se
explica por rango, codificación ni disponibilidad. Además: IC bootstrap de C_obs (resampleo de soportes).

Uso:  TF_FAMILY="Indo-European" python3 src/nulls.py     (env TF_B nº simulaciones, def 500)
"""
import os, sqlite3, random
import panphon
from universes import load, span_membership, PRIM, delta, is_cons

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "data", "db", "transf.db")
FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
MINEDGE = 30
B = int(os.environ.get("TF_B", "500"))


def cofO(ops):
    s = set(ops); n = len(ops); real = 0
    for i in range(n):
        for j in range(i + 1, n):
            if (ops[i] ^ ops[j]) in s:
                real += 1
    return real / (n * (n - 1) // 2) if n > 1 else 0.0


def enum_span(O):
    """enumera ⟨O⟩\\{0} como lista de frozensets de rasgos."""
    used = [r for r in PRIM if any(r in d for d in O)]
    idx = {r: i for i, r in enumerate(used)}
    basis = []
    for d in O:
        v = sum(1 << idx[r] for r in d)
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    out = []
    for bits in range(1, 1 << len(basis)):
        v = 0
        for k in range(len(basis)):
            if bits >> k & 1:
                v ^= basis[k]
        out.append(frozenset(used[i] for i in range(len(used)) if v >> i & 1))
    return out


def weight_pool(used, wmax=3):
    import itertools
    pool = []
    for w in range(1, wmax + 1):
        for combo in itertools.combinations(used, w):
            pool.append(frozenset(combo))
    return pool


def sample_distinct(pool, k, rng):
    return rng.sample(pool, min(k, len(pool)))


def null_swap(O, rng, steps=2000):
    """Nulo 2: swap-MCMC sobre la matriz incidencia operador×rasgo preservando sumas de fila y columna."""
    used = [r for r in PRIM if any(r in d for d in O)]
    M = [set(d) for d in O]                     # filas como conjuntos de rasgos
    for _ in range(steps):
        i, j = rng.randrange(len(M)), rng.randrange(len(M))
        if i == j:
            continue
        Ai, Aj = M[i] - M[j], M[j] - M[i]       # rasgos exclusivos de cada fila
        if not Ai or not Aj:
            continue
        a = rng.choice(list(Ai)); b = rng.choice(list(Aj))
        # swap a<->b preserva tamaño de fila y sumas de columna
        M[i] = (M[i] - {a}) | {b}
        M[j] = (M[j] - {b}) | {a}
    return [frozenset(x) for x in M]


def stats(vals, obs):
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5
    z = (obs - mu) / sd if sd else 0.0
    p = (1 + sum(1 for v in vals if v >= obs)) / (len(vals) + 1)
    return mu, sd, z, p


def main():
    O, Omega, U, S = load()
    Oset = set(O)
    obs = cofO(O)
    used = [r for r in PRIM if any(r in d for d in O)]
    span = enum_span(O)
    pool0 = weight_pool(used, 3)
    rng = random.Random(2024)

    nulls = {
        "0 tamaño+peso≤3": lambda: sample_distinct(pool0, len(O), rng),
        "1 pesos Hamming ": None,     # se maneja aparte (preserva multiconjunto de tamaños)
        "2 marginales exac": lambda: null_swap(O, rng),
        "3 span ⟨O⟩       ": lambda: sample_distinct(span, len(O), rng),
        "4 realizable U_S ": lambda: sample_distinct(list(U), len(O), rng),
        "5 oportunidad Ω_D": lambda: sample_distinct(list(Omega), len(O), rng),
    }

    # nulo 1: preservar tamaños exactos, muestreando cada operador como subconjunto aleatorio de ese tamaño
    sizes = [len(d) for d in O]
    def draw_null1():
        seen = set()
        for sz in sizes:
            for _ in range(30):
                import itertools
                cand = frozenset(rng.sample(used, sz))
                if cand not in seen:
                    seen.add(cand); break
        return list(seen)

    print(f"\n=== V4-4 · Jerarquía de nulos para C(O) · {FAMILY}  (B={B}) ===")
    print(f"C(O) observado = {obs:.3f}   (|O|={len(O)}, rango {len(span).bit_length() if span else 0})\n")
    print(f"  {'nulo':18} {'E[C]':>7} {'sd':>6} {'Z':>7} {'p_MC':>7}")
    order = ["0 tamaño+peso≤3", "1 pesos Hamming ", "2 marginales exac", "3 span ⟨O⟩       ",
             "4 realizable U_S ", "5 oportunidad Ω_D"]
    for name in order:
        vals = []
        for _ in range(B):
            samp = draw_null1() if name.startswith("1") else nulls[name]()
            vals.append(cofO(samp))
        mu, sd, z, p = stats(vals, obs)
        flag = "  ***" if p < 0.05 else ""
        print(f"  {name:18} {mu:7.3f} {sd:6.3f} {z:+7.2f} {p:7.3f}{flag}")

    # bootstrap IC de C_obs: resampleo Poisson de soportes y re-umbral
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT a,b,count FROM lex_correspondence WHERE family=? AND kind='signal'", (FAMILY,)).fetchall()
    con.close()
    base = []
    for a, b, c in rows:
        if a != b and is_cons(a) and is_cons(b):
            d = delta(a, b)
            if d: base.append((d, c))
    boot = []
    for _ in range(B):
        acc = {}
        for d, c in base:            # Poisson(c) resample de cada conteo, luego re-umbral
            k = _poisson(rng, c)
            acc[d] = acc.get(d, 0) + k
        Ob = [d for d, k in acc.items() if k >= MINEDGE]
        if len(Ob) > 1:
            boot.append(cofO(Ob))
    boot.sort()
    lo, hi = boot[int(0.025*len(boot))], boot[int(0.975*len(boot))]
    print(f"\nIC bootstrap 95% de C(O) (resampleo Poisson de soportes): [{lo:.3f}, {hi:.3f}]  (obs {obs:.3f})")
    print("\nLectura: C(O) es hallazgo SÓLIDO solo si sobrevive a los nulos 3–5 (rango, realizable, oportunidad).")


def _poisson(rng, lam):
    import math
    if lam > 30:                      # aproximación normal (Knuth es O(lam), impracticable para λ grande)
        return max(0, int(round(lam + (lam ** 0.5) * rng.gauss(0, 1))))
    L = math.exp(-lam); k = 0; p = 1.0
    while True:
        k += 1; p *= rng.random()
        if p <= L:
            return k - 1


if __name__ == "__main__":
    main()
