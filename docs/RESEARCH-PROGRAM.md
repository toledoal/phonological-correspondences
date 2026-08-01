# Research programme — the empirical geometry of phonological correspondences

**Alejandro Toledo Martínez** — Independent researcher ([ORCID 0009-0000-1277-9697](https://orcid.org/0009-0000-1277-9697))
· 1 August 2026 · CC BY 4.0 · companion to the paper and manual *Additive Structure of Phonological
Correspondences* · code: https://github.com/toledoal/phonological-correspondences

*This is a programme document, not a results paper. It states the vision, what the pilot has and has not
established, the central falsifiable claim, and a staged agenda of concrete studies — each with a method, a
success criterion, and a disconfirming outcome. It also absorbs the findings of the adversarial review round
(`docs/reviews/adversarial-synthesis.md`) as Workstream 0.*

---

## 1. The vision

Historical linguistics infers a hidden past (protoforms, sound laws, trees) from documented forms. This
programme **inverts the order of inference**: it first discovers *mathematical structure* in attested forms —
with no protoforms, no sound laws, no imposed sound classes — and only afterwards contrasts that structure with
the historical apparatus, which never entered the computation. The unit of study is the **operator**: the set of
phonological features by which two aligned segments differ. A language system then becomes an **empirical
repertoire** of such operators — a measurable region of a feature space, with a geometry, an additive structure,
and a set of pointed absences. The long-term aim is a **science of the empirical geometry of sound
correspondences**: what regions languages occupy, why, how systems differ, and how — brought in last — this maps
onto history, typology, and the design of language models.

## 2. What the pilot established (and did not)

On two families (Indo-European, Austronesian), reconstruction-free from Lexibank:

**Survives scrutiny (with stated scope):**
- The **occupancy reframe**: sparsity is mostly *algebraic* (a vast span), not linguistic; measured against the
  differences the corpus makes available, repertoires are fairly *dense*.
- **Additive structure above size-matched chance**: the composition index $C(O)$ and companion measures
  ($\tau,\kappa,E$) exceed six nested null models, up to sampling from the corpus's own opportunity set.
- A clean separation of **representation vs data**: e.g. the one Austronesian linear dependency is a property of
  the *selected* repertoire, not of the feature chart.
- A concrete **geometry of holes** ($\langle O\rangle\setminus O$): available-but-unchosen operators.
- The **grouping-null** control on branches, and the **two-level** (pair vs type) cognacy validation.

**Explicitly not established (honest scope):**
- The additive structure is **representational, not genealogical** at the type level (a concept-permuted control
  matches it). Genealogical signal, if any, lives in *distributions*, not type sets.
- All cross-family contrasts rest on **$n=2$** families — anecdotal, not inferential.
- "Reconstruction-free" means **protoform- and sound-law-free**; statistical cognacy (LexStat) still encodes a
  correspondence prior. The opportunity universe $\Omega_D$ is corpus-and-aligner-dependent.

## 3. The central claim and how to kill it

> **Central claim.** Documented languages occupy sparse, additively-structured, low-effective-dimensional
> regions of the feature-difference space, and these regions carry measurable structure *beyond* what the
> segment inventory and the feature representation alone impose.

**Disconfirming outcomes (pre-registered in spirit):**
1. If, across many families, the observed additive/geometric measures are **statistically indistinguishable from
   the concept-permuted artifact $D_R$ and from inventory-matched controls**, then the "structure" is entirely
   representational and the claim's second clause fails.
2. If **language-level resampling** (not support resampling) makes the additive signal vanish, it was a
   support-counting artifact.
3. If, under the **historical-holdout** protocol (§Workstream 8), blind operator-distribution clustering recovers
   *nothing* that aligns with independently-known families/areas beyond chance across many families, the
   distributional-signal claim fails.

Stating these makes the programme falsifiable; "a non-match is also informative" (used elsewhere) is a statement
about *diagnosis*, not a licence to treat every outcome as success.

## 4. Workstreams

### W0 — Consolidate and harden the pilot *(immediate; from the adversarial review)*
- **Scholarship:** add a Related Work section and full references (LingPy/List; panphon/Mortensen; Lexibank/List;
  IE-CoR/Heggarty et al. 2023; Glottolog/Hammarström; Concepticon; ASJP; Jäger; Blasi et al.; additive
  combinatorics; matroid/coding theory). Reframe "reconstruction-free" honestly.
- **Estimation:** replace the support bootstrap with a **language-level** bootstrap/jackknife (valid for a
  U-statistic over non-independent pairs); report BCa intervals; add **FDR** control across the nulls × families
  × measures grid; raise simulation count so $p_{MC}$ is informative.
- **Sensitivity:** support threshold, weight cap, and feature subset swept (DONE, `make sensitivity`): headlines
  invariant (C(O), rank, occupancy stable well above the null across all three). LexStat-threshold and aligner
  sweeps (need corpora) still scheduled. Document the exact **12-feature** subselection (or move to a standard panphon set).
- **Ternary rigour:** define $\Delta$ as the indicator vector (drop the ill-typed "$=\phi\oplus\phi$"); recompute
  the invariants under the **typed-space** model of manual Ch.13 and show stability.
- **Bias disclosure:** quantify the weight-$\le3$ cap's effect on $C(O),\tau,\kappa,E$; scope "basis-independent"
  claims to span/rank; report circuit/hole counts **normalized** for $|O|$.
- **Independence of $\Omega_D$:** derive the opportunity universe from an independent segment/co-occurrence source
  and bound the tautological part of $\rho_{\rm opp}$ and $C_\Omega$.
- **Data hygiene:** replace non-cognate worked sets ('fire', 'star') with genuine single-etymon sets; settle a
  per-family **vowel policy** (drop "ablaut noise"); flag creole/known-loan forms.
- **Validation coverage:** obtain a gold-cognacy resource for Austronesian (ABVD cognate sets) so type-level
  precision is not an IE-only claim.

### W1 — From $n=2$ to a comparative sample
Run the full pipeline on **20–50 families** with adequate Lexibank coverage. Only here do cross-family statements
become inferential. Deliverable: a cross-family table of rank, occupancies, $C(O)$-vs-null, atom inventories,
matroid signatures — with proper controls. Question: *are there family-independent regularities in the geometry,
or is every system its own shape?*

### W2 — The directed, context-conditioned layer (where laws live)
Build the tensor $X_{ijo}$ (operator frequency by language pair) and $X_{ijoc}$ (adding context: neighbours,
position, stress, morphology). Non-negative factorization surfaces **operator bundles over language sets**;
**Minimum Description Length** turns "a compressive context-conditioned bundle" into an operational definition of
an *emergent rule*. Success criterion: recover known sound laws (e.g. Grimm, Grassmann, Verner, Polynesian
lenition) as compressive factors **without** having supplied them. Falsifier: no factor aligns with any known law
better than chance.

### W3 — Distributions and the genealogical signal
The pilot located the genealogical signal in distributions, not type sets. Quantify it properly: mutual
information $I(O;\text{branch})$ **controlled** for per-branch inventory and sample depth; distributional
distances between languages; whether the language graph $G_L$ recovers branches. Question: *how much history is
recoverable from operator frequencies alone, and at what taxonomic depth does it wash out?*

### W4 — Loans and contact
Using a loan-annotated corpus (**WOLD**), test the idea that a borrowing is not an annotation but something that
either **moves or does not move** the system's repertoire: does removing loan-flagged forms change $O$, $C(O)$,
the distribution? Question: *is "cognate vs loan" visible as a structural, not just philological, distinction?*

### W5 — Time without reconstruction
The corpus mixes ancient and modern states. Use **documented dates** (not reconstructed ancestors) to study how a
family's repertoire changes over attested time: a temporal network $G(t)$, repertoire drift, whether occupancy
and additive density move monotonically. Question: *can we see the geometry evolve without positing a proto-node?*

### W6 — Family-blind typology *(later phase; deliberately deferred)*
Cluster languages by operator distribution with **no** genealogical labels (Wasserstein ground distance over
operators). Ask what systems emerge — trees, networks, continua, areal blocks. This targets the *universal*
questions the intra-system pilot deliberately avoids; it belongs after W1–W3 so that "system" is earned, not
assumed.

### W7 — The deeper mathematics
Take the additive-combinatorics / matroid / coding-theory framing from metaphor to theorem: is $O$ near an
**affine** subspace (direct test, not inferred from low $\kappa$)? What do the **matroid** and its circuits say
about cross-family dependency structure (same dependencies under different feature names)? **Persistent topology**
of the composition complex ($u\oplus v=w$ triangles across a frequency threshold); **spectral** signatures of
$G_S/G_O$. Question: *which mathematical objects are the right invariants of a phonological system?*
A concrete sub-item: **the order/permutation dimension (metathesis).** Present operators live in feature space
$\mathbb F_2^n$ at aligned slots; a monotonic aligner cannot represent a *reordering* of segments (TR↔RT), so
metathesis is currently mis-scored as substitutions+gaps. Add it as a first-class second dimension — an operator
carries a feature-change *and* a permutation of skeleton positions (the symmetric group $S_k$ beside
$\mathbb F_2^n$) — detected alignment-free by same-multiset/different-order skeletons, and measured by permutation
distance. This is the mirror-inversion the consonantal-skeleton view was designed to catch.

### W8 — The historical-holdout protocol
Formalize discovery → stability → **blind** system discovery → external contrast (paper §6; manual Ch.20) and run
it end-to-end on W1's sample, reporting adjusted Rand index / normalized mutual information against
independently-known families and areas. This is the programme's methodological spine and its main guard against
circularity.

### W9 — Connections to language models *(exploratory)*
Two threads: (a) **representation** — do feature-additive, low-rank/affine priors help models of sound structure?
(b) **evaluation** — the "discover-first, admit labels only to test" discipline as a template for leakage-free
evaluation of models on historical/typological tasks (a model that "recovers Grimm" counts only if the law was
never in its inputs).

### W10 — The reserved apparatus (OAS, protoforms)
Kept out of discovery on principle. The only admissible use is as an **external partition under a blind test**:
*do the dimensions/communities/latent factors discovered from IPA and correspondences spontaneously recover
groupings compatible with OAS (or with reconstructions)?* Recovery is independent evidence; non-recovery lets the
external scheme be revised without circularity. **OAS is not used as a coordinate anywhere in W0–W9.**

## 5. Phased roadmap

| Phase | Focus | Workstreams | Main deliverable |
|---|---|---|---|
| **1 — Consolidate** | make the pilot bullet-proof | W0 | revised paper + manual with references, honest scope, hardened statistics |
| **2 — Scale & direct** | earn inferential claims; find emergent laws | W1, W2, W3 | cross-family study; directed-tensor/MDL "emergent laws" paper |
| **3 — Contact & time** | dynamics and borrowing | W4, W5 | loan-influence study; documented-time drift study |
| **4 — Typology & math** | universals, deeper invariants | W6, W7, W8 | family-blind typology; mathematical-invariants paper; holdout benchmark |
| **5 — Transfer** | AI and the reserved schemes | W9, W10 | LM representation/eval note; blind-test of OAS/reconstructions |

## 6. Success criteria and falsifiers (summary)

| Claim | Success looks like | Disconfirmed if |
|---|---|---|
| Structure beyond representation | measures exceed $D_R$ + inventory controls across many families | indistinguishable from $D_R$ across families |
| Signal is real, not resampling | survives language-level bootstrap | vanishes under language resampling |
| Laws can emerge | known laws recovered as MDL/NMF factors, unsupplied | no factor beats chance vs known laws |
| History lives in distributions | $G_L$/MI recovers branches above chance (controlled) | no better than inventory-matched null |
| Mathematics is the right lens | stable invariants (rank, matroid, affineness) across families | invariants are artifacts of binarization / weight cap |

## 7. What would make this a field, not a paper

A shared, reproducible pipeline (already public); a growing atlas of family repertoires with controls; an agreed
set of invariants and null models; and a validation protocol (W8) that any newcomer can run. The measure of
success is not a single result but whether **others can pose and answer new questions in these terms** — about
any language system, without first committing to a reconstruction.
