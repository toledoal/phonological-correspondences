# Additive Structure of Phonological Correspondences

### A protoform-agnostic method for discovering mathematical patterns in documented linguistic systems

**Alejandro Toledo Martínez** — Independent researcher (ORCID: 0009-0000-1277-9697)

**Preprint · pilot study · 31 July 2026 · License: CC BY 4.0**

*Companion manual:* "Additive Structure of Phonological Correspondences: A Manual" (DOI: pending). *Code &
reproducible pipeline:* (repository / Zenodo DOI: pending).

*How to cite:* Toledo Martínez, A. (2026). *Additive Structure of Phonological Correspondences: A
protoform-agnostic method for discovering mathematical patterns in documented linguistic systems.* Preprint
(DOI: pending).

---

## Abstract

Historical linguistics infers ancestral forms and then derives documented ones from them. We invert that order.
Representing each attested sound correspondence not as a directed change but as the **set of phonological features
that differ** between two aligned segments — a symmetric *operator* — a language family becomes a **repertoire**
$O$ of feature-difference vectors over $\mathbb F_2$, computed with no reconstruction, no sound laws, and no
externally imposed sound classes. We study the geometry and additive structure of $O$ for Indo-European (IE) and
Austronesian (AN), drawn reconstruction-free from Lexibank via statistical cognacy (LexStat) and
feature-distance alignment (panphon). Four results. (i) **Occupancy is not sparsity of the languages but vastness
of the space:** of the differences the corpus actually makes available, IE realizes 63% and AN 48%. (ii) The
repertoire is **additively organized** — combining two operators lands back in $O$ far more often than chance,
and this survives a hierarchy of six nested null models up to and including sampling from the corpus's own
opportunity set ($Z=+6.3$ IE, $+5.9$ AN; $p_{\mathrm{MC}}\le0.004$). (iii) That additive structure is a property
of the **phonological representation**, not of genealogy: a concept-permuted control matches it, and branch
repertoires overlap no more than random language groupings in IE (though they do in AN). (iv) The
**generable-but-unattested** operators $\langle O\rangle\setminus O$ form a concrete geometry of near-misses.
The contribution is not a sound law but an *object of study* — the empirical repertoire of correspondences and
its measurable additive geometry — together with an inference order that keeps the historical apparatus out of
the computation so it can serve as an independent test. A companion manual gives the full didactic treatment.

---

## 1. Introduction

The comparative method is an inference toward a hidden past: from documented forms $X$ it reconstructs an
ancestor $\widehat Z$ and posits the changes $H$ that produced $X$. It answers *how did these forms descend from
their common ancestor?* We ask a different question — *treated purely as a set of differences, what shape does
the space of attested correspondences have?* — and we answer it in the opposite order:
$$X \longrightarrow \mathcal M(X), \qquad\text{then, separately,}\qquad \mathcal M(X)\longleftrightarrow H,$$
where $\mathcal M(X)$ is a mathematical structure discovered without protoforms or precoded laws, and the
historical apparatus enters only *afterward*, as contrast. This is not a rejection of reconstruction; it is a
more demanding test of it. Protoforms are inferred *from* the documented languages; building the space *on* them
and then checking whether it confirms historical regularities risks circularity — leakage of the target into the
inputs. Suspending them during discovery is therefore a design choice, not a limitation.

Two clarifications frame everything below. First, the method is not "theory-free": transcription, segmentation,
concept assignment, the feature matrix, and the aligner are measurement instruments whose influence we make
explicit and control for (§3, §4.3). Second, this is emphatically **not** a claim that "sound change is XOR," nor
a hunt for known sound laws; it is a change of what is measured and in what order.

## 2. The operator and the repertoire

For two aligned segments $a,b$ with panphon feature map $\phi$, the **operator** is the symmetric
feature-difference
$$\Delta(a,b)=\{k:\phi_k(a)\neq\phi_k(b)\}\;=\;\phi(a)\oplus\phi(b)\ \ (\text{over binary features}).$$
It is a *contrast*, not a directed change: $\Delta(a,b)=\Delta(b,a)$, so $\Delta$ does not distinguish
$t\!\to\!s$ from $s\!\to\!t$, and "each operator is its own inverse" is a consequence of that symmetry, not a
phonological finding. Directed history, when wanted, requires a richer object
$T=(a,b,c,p,\ell_1,\ell_2,w)$ with signature $\sigma(T)=\Delta(a,b)$; this paper studies the symmetric
signatures. We keep operators of one to three features (**atoms** and small **molecules**).

A family's **repertoire** $O$ is its set of recurrent operators. $O$ generates a subspace
$\langle O\rangle=\operatorname{span}_{\mathbb F_2}(O)$ of dimension (rank) $r$; crucially $O$ is **not** a
subspace (not closed under XOR, does not contain $0$) — it is a *region*, and the object of interest is the
relation between the region $O$ and the capacity $\langle O\rangle$.

## 3. Data and method

**Corpus.** Lexibank word lists, IPA-segmented, for Indo-European (304 languages available) and Austronesian
(978), taking per family the languages with the most forms. **Cognacy** is detected statistically with LexStat
(LingPy); **alignment** is Needleman–Wunsch with substitution cost equal to the fraction of panphon features that
differ; **features** are panphon's primary set (12 features including labiality). No protoforms, laws, or sound
classes enter the computation. Operators are taken from aligned, non-identical, consonantal positions (vowels are
ablaut noise) with support thresholds (30 at family scale). Independent validation uses IE-CoR expert cognacy
(§4.6). Every quantity is reproducible from a single `make` target (§7).

Two families give a minimal comparative frame; "IE" and "AN" are pilot genealogical boundaries, not results.

## 4. Results

### 4.1 Occupancy: sparsity is mostly algebraic

IE uses $|O|=67$ operators, AN $|O|=22$, with ranks $r=12$ and $r=10$. Against the full algebraic span these are
1.6% and 2.2% — but the span $2^r-1$ contains feature-bundles that no pair of real segments could realize. Nested
between $O$ and $\langle O\rangle$ are the **realizable** universe $U_S=\{\Delta(a,b):a,b\in S\}$ (over the
attested segment inventory $S$) and the **opportunity** universe $\Omega_D$ (differences that actually occur in
aligned corpus positions):

| family | $\rho_{\mathrm{alg}}$ (vs span) | $\rho_{\mathrm{seg}}$ (vs realizable) | $\rho_{\mathrm{opp}}$ (vs opportunity) |
|---|---|---|---|
| Indo-European | 0.016 | 0.48 | **0.63** |
| Austronesian | 0.022 | 0.43 | **0.48** |

where $\rho_{\mathrm{alg}}=\lvert O\rvert/(2^r-1)$, $\rho_{\mathrm{seg}}=\lvert O\rvert/\lvert U_S\cap\langle
O\rangle\rvert$, and $\rho_{\mathrm{opp}}=\lvert O\rvert/\lvert\Omega_D\cap\langle O\rangle\rvert$. Of what was
actually available, the repertoire is *dense*, not sparse: the "98% unused" is the algebraic space being
enormous, not languages being restrictive.

### 4.2 The repertoire is additively organized

Composing two operators is XOR of their feature-sets. The **composition-realization index**
$$C(O)=\frac{|\{\{u,v\}\subseteq O:u\oplus v\in O\}|}{\binom{|O|}{2}}$$
is $0.220$ (IE) and $0.234$ (AN); conditioned on the opportunity universe, $C_\Omega(O)=0.81$ (IE), $0.66$ (AN).
To test whether this exceeds chance we compare against a hierarchy of null repertoires, each preserving more
structure and each sampled to size $|O|$; we report $Z$ and empirical $p_{\mathrm{MC}}$ over 500 simulations:

| null preserves | IE $Z$ | AN $Z$ |
|---|---|---|
| size + weight $\le3$ | +15.7 | +12.0 |
| Hamming weights | +14.8 | +9.0 |
| exact margins (swap-MCMC) | +7.5 | +3.6 |
| rank / span $\langle O\rangle$ | +45.6 | +13.7 |
| realizable $U_S$ | +9.2 | +7.3 |
| **opportunity $\Omega_D$** | **+6.3** | **+5.9** |

All six survive at $p_{\mathrm{MC}}\le0.004$: even drawn from exactly the differences the corpus made available,
the observed repertoire is significantly more composition-closed. Three further additive statistics agree
(against the $\Omega_D$ null): triple density $\tau$ is high (IE $Z{=}{+}6.6$, AN ${+}6.5$), the doubling constant
$\kappa=|O\oplus O|/|O|$ is low (IE $Z{=}{-}5.1$, AN ${-}6.0$), and additive energy $E$ is high (IE ${+}7.4$, AN
${+}7.3$). The repertoire behaves like an approximate (possibly affine) subspace. Its dependency structure has a
basis-independent core: as a binary matroid it has 162 (IE) and 18 (AN) three-element circuits, with `{voi}`
(voicing) the most-connected operator in both — the additive hub.

### 4.3 What the additive structure is — and is not

The structure of §4.2 is a property of the phonological **representation and inventory**, not of genealogy or
semantics. Two controls establish this. First, permuting concept labels to destroy all cognacy and semantic
linkage (regime $D_R$) yields additive structure *as high as or higher than* expert cognacy $D_G$
($C{=}0.215$ vs $0.169$), so the type-level additive closure does not distinguish history from inventory.
Second, the one linear dependency we observe — in AN, `ant`$\,=\,$`cor`$\oplus$`lab` — is a property of the
*selected* repertoire, not of the feature matrix: the realizable universe $U_S$ has full rank (12, corank 0), so
the ontology would permit independence; the dependency appears only in $O_{\mathrm{AN}}$. The additive geometry
is real (§4.2) but must be read as *representational*; genealogical signal lives elsewhere (§4.5–4.6).

### 4.4 The geometry of holes $\langle O\rangle\setminus O$

Among the operator-shaped (weight $\le3$) vectors the span generates, most are **holes** — generable but
unattested. For each hole $x$, its depth is $d(x,O)=\min_{o\in O}d_H(x,o)$.

| | generable (weight $\le3$) | observed | holes | at $d=1$ | holes in $\Omega_D$ |
|---|---|---|---|---|---|
| Indo-European | 298 | 67 | 231 | 160 | 40 |
| Austronesian | 119 | 22 | 97 | 53 | 24 |

Most holes lie one feature from an attested operator; the linguistically loaded ones are the **holes in
$\Omega_D$** (40 IE, 24 AN) — differences the corpus made available yet the system left unused. These are the
concrete candidates for interpretation: absences that are choices, not impossibilities.

### 4.5 Systems and branches

Partitioning each family into Glottolog branches and taking $O_F=\bigcup_r O_r$, the persistence histogram $H_k$
(operators in exactly $k$ branches) decomposes the repertoire without double-counting: IE $|O_F|=97$, strict
nucleus $K_\cap=12$ (the atoms `{ant} {cont} {voi}` in every branch), majority nucleus $K_{1/2}=38$; AN
$|O_F|=48$, $K_\cap=4$, $K_{1/2}=18$. But raw branch overlap is uninterpretable without a null. Against a
**grouping null** (arbitrary same-size language groups) the mean Jaccard tells opposite stories in the two
families:

| | mean Jaccard (real branches) | arbitrary groupings | $Z$ |
|---|---|---|---|
| Indo-European | 0.42 | $0.45\pm0.05$ | $-0.7$ (indistinguishable) |
| Austronesian | 0.51 | $0.57\pm0.01$ | $-5.4$ (real branches more differentiated) |

At the level of operator **types**, Indo-European branches share no more than random groupings — the apparent
"shared core" is shared *inventory* — whereas Austronesian branches are significantly more differentiated than
chance. Under rarefaction the nucleus size is sample-sensitive, so branch *richness* is not interpreted; the
robust facts are the histogram decomposition and the grouping-null contrast.

### 4.6 Validation against expert cognacy

Statistical cognacy could contaminate the repertoire with false cognates. Against IE-CoR expert cognacy the
contamination is real at the **instance** level (pair precision 0.73, recall 0.33) but absorbed at the **type**
level: LexStat's operator inventory has precision $\approx1.0$ and recall $0.66$ against the expert repertoire —
a false cognate almost always produces an operator already present. The type inventory is thus more robust than
individual cognate identification. Where genealogical signal does live is the **distributions**: mutual
information between operator and branch is modest but non-zero and larger in AN than IE ($0.22$ vs $0.14$
normalized), consistent with §4.5; a few operators dominate each family (effective count $N_{\mathrm{eff}}=24$ of
119 IE, $18$ of 63 AN).

## 5. Figures

```latex
\input{fig-graph-ie}
```

```latex
\input{fig-graph-an}
```

```latex
\input{fig-opgraph-ie}
```

## 6. Discussion

The contribution is an **object** and an **order**. The object is the empirical repertoire $O$ of symmetric
feature-difference operators, and the separation between it and the subspace $\langle O\rangle$ it generates: a
system uses a small, additively-structured region of a large algebraic space, densely relative to opportunity,
with a concrete geometry of unused near-misses. The order is discover-then-contrast, which keeps reconstructions,
laws, and sound classes out of the measurement so each can serve as an independent yardstick later.

Two boundaries keep the claims honest. The additive structure is *representational*, not genealogical (§4.3);
the genealogical question is properly posed on **distributions** and, in future work, on a directed,
context-conditioned layer — the tensor $X_{ijoc}$ of operator frequency by language pair and context, whose
non-negative factorization and minimum-description-length rules would let sound laws *emerge* as compressive
bundles rather than be inserted. Under a **historical-holdout** protocol (discover; test stability; cluster
languages blind; only then compare to reconstructions and trees), a recovered law would be evidence precisely
because it was never an input. The same discipline — discover structure first, admit ground-truth labels only to
test — is a template for leakage-free evaluation of language models on historical and typological tasks.

## 7. Limitations and reproducibility

**Limitations.** Two families are a pilot; "family" is a genealogical label taken as a boundary, not a result.
The opportunity universe $\Omega_D$ and the additive nulls depend on the corpus and aligner. The additive
structure is type-level and representational; loans-as-system-influence could not be tested (loan annotations are
absent in the pilot corpora and require a resource such as WOLD). Force-directed figures lack an articulatory
coordinate system. None of these affect the null-controlled results, but they bound their interpretation.

**Reproducibility.** All results run from `transformations/src` against a repertoire built by
`make family FAMILY="X"`. Key targets: `make universes` (§4.1), `make nulls` / `make additive` (§4.2, §4.4),
`make repr-control` (§4.3), `make superposition` (§4.5), `make cognate-eval` / `make distributions` (§4.6).
Datasets: Lexibank, IE-CoR, Glottolog (cached classification). LexStat threshold 0.55, 100-run scorer; panphon
12-feature primary set; seeds fixed. The companion **manual** (`docs/manual`) gives worked, hand-computed
examples of every measure and the full derivations.
