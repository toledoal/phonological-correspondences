#!/usr/bin/env python3
"""V4-5 · Combinatoria aditiva, circuitos del matroide y geometría de huecos (revisión colaborativa §4.1–4.3).

Sobre el repertorio observado O (frozensets de rasgos = vectores de F_2^n bajo XOR):

  · Densidad de triples   τ(O) = |{(u,v,w)∈O³ : u⊕v=w}| / |O|²
  · Conjunto suma         O⊕O = {u⊕v}                     · Duplicación κ = |O⊕O|/|O|  (chica ⇒ estructura fuerte)
  · Energía aditiva       E(O) = |{(a,b,c,d)∈O⁴ : a⊕b=c⊕d}| = Σ_s r(s)²,  r(s)=|{(a,b):a⊕b=s}|
  · Circuitos del matroide: conjuntos mínimos con XOR=0 (tamaño 3: u⊕v⊕w=0; tamaño 4).
  · Código lineal ⟨O⟩ y GEOMETRÍA DE HUECOS: entre los operadores generables (peso≤3) del span, ¿cuáles NO se
    observan, y a qué distancia de Hamming del repertorio están? (huecos cercanos d=1 vs profundos).

τ/κ/E se comparan contra un nulo que muestrea |O| de Ω_D (oportunidad). Uso: TF_FAMILY="…" python3 src/additive.py
"""
import os, random, itertools
from collections import Counter
from universes import load, span_membership, PRIM
from nulls import enum_span

FAMILY = os.environ.get("TF_FAMILY", "Indo-European")
B = int(os.environ.get("TF_B", "300"))


def sumset(O):
    return {u ^ v for u in O for v in O}


def tau(O):
    s = set(O); n = len(O)
    cnt = sum(1 for u in O for v in O if (u ^ v) in s)
    return cnt / (n * n) if n else 0.0


def energy(O):
    r = Counter()
    for u in O:
        for v in O:
            r[u ^ v] += 1
    E = sum(c * c for c in r.values())
    return E, E / (len(O) ** 3) if O else 0.0        # normalizada por |O|³ (∈[1/|O|,1])


def kappa(O):
    return len(sumset(O)) / len(O) if O else 0.0


def circuits3(O):
    s = set(O); L = list(O); seen = set(); c = 0; part = Counter()
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            w = L[i] ^ L[j]
            if w in s and w != L[i] and w != L[j]:
                key = frozenset((L[i], L[j], w))
                if len(key) == 3 and key not in seen:
                    seen.add(key); c += 1
                    for o in key:
                        part[o] += 1
    return c, part


def main():
    O, Omega, U, S = load()
    Ol = list(O)
    print(f"\n=== V4-5 · Combinatoria aditiva y huecos · {FAMILY} ===")
    print(f"|O| = {len(Ol)}\n")

    # 1) medidas aditivas + nulo (muestrear |O| de Ω_D)
    t, (E, En) = tau(Ol), energy(Ol)
    k = kappa(Ol)
    rng = random.Random(99)
    pool = list(Omega)
    nt, nk, ne = [], [], []
    for _ in range(B):
        samp = rng.sample(pool, min(len(Ol), len(pool)))
        nt.append(tau(samp)); nk.append(kappa(samp)); ne.append(energy(samp)[1])
    def z(obs, arr):
        mu = sum(arr)/len(arr); sd = (sum((x-mu)**2 for x in arr)/len(arr))**0.5
        return mu, (obs-mu)/sd if sd else 0.0
    mt, zt = z(t, nt); mk, zk = z(k, nk); me, ze = z(En, ne)
    print("1) MEDIDAS ADITIVAS (obs vs nulo Ω_D):")
    print(f"   τ(O)  densidad de triples = {t:.4f}   nulo {mt:.4f}  Z={zt:+.1f}")
    print(f"   κ(O)  duplicación        = {k:.2f}     nulo {mk:.2f}  Z={zk:+.1f}   (menor = más estructura aditiva)")
    print(f"   E(O)  energía normaliz.  = {En:.4f}   nulo {me:.4f}  Z={ze:+.1f}")

    # 2) circuitos del matroide
    c3, part = circuits3(Ol)
    print(f"\n2) MATROIDE — circuitos de tamaño 3 (u⊕v⊕w=0): {c3}")
    if part:
        top = " · ".join("{"+"+".join(sorted(o))+"}"+f":{n}" for o, n in part.most_common(6))
        print(f"   operadores en más circuitos: {top}")

    # 3) código lineal y geometría de huecos
    span = enum_span(Ol)                 # ⟨O⟩\{0}, cualquier peso
    r = len(span).bit_length()
    G = [d for d in span if len(d) <= 3]      # operadores GENERABLES con forma de operador (peso≤3)
    holes = [d for d in G if d not in set(Ol)]
    def dH(x, y): return len(x ^ y)           # distancia de Hamming entre operadores (XOR de rasgos)
    depth = Counter()
    in_opp = 0
    Oset = set(Ol)
    for h in holes:
        dmin = min(dH(h, o) for o in Ol)
        depth[dmin] += 1
        if h in Omega: in_opp += 1
    wdist = Counter(len(d) for d in Ol)
    print(f"\n3) CÓDIGO LINEAL ⟨O⟩ (rango {r}) y GEOMETRÍA DE HUECOS:")
    print(f"   distribución de pesos de O: " + " · ".join(f"peso{w}:{wdist[w]}" for w in sorted(wdist)))
    print(f"   operadores generables con forma de operador (peso≤3) en ⟨O⟩: {len(G)}  →  observados {len(Ol)}, "
          f"HUECOS {len(holes)}")
    print(f"   profundidad de huecos d(x,O): " + " · ".join(f"d={k}:{depth[k]}" for k in sorted(depth)))
    print(f"   huecos cercanos (d=1, ausentes por UN rasgo): {depth.get(1,0)}   ·   "
          f"huecos que YA están en la oportunidad Ω_D (ausentes pese a ser realizables): {in_opp}")
    print(f"\nLectura: κ pequeña y τ/E altas frente al nulo ⇒ O tiene estructura aditiva (cerca de subespacio/afín).")
    print("Los huecos d=1 son los operadores 'a un rasgo' de completar el patrón; los que están en Ω_D son")
    print("ausencias reales (disponibles pero no elegidas), candidatos a interpretación lingüística.")


if __name__ == "__main__":
    main()
