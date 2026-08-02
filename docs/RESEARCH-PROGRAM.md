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
- **Estimation:** language-level bootstrap DONE (`make bootstrap-lang`, percentile CI, results in data/results/): C(O) robust in IE [0.18,0.22], fragile in AN [0.15,0.30]. Still open: BCa/jackknife intervals, FDR across the nulls × families × measures grid, larger simulation count.
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
**A dedicated future line — the mathematics of metathesis.** Present operators live in feature space
$\mathbb F_2^n$ at aligned slots; a monotonic aligner cannot represent a *reordering* of segments (TR↔RT), so
metathesis is currently mis-scored as substitutions+gaps. It should become a first-class second dimension: an
operator carries a feature-change *and* a **permutation of skeleton positions** — the symmetric group $S_k$
beside $\mathbb F_2^n$ — detected alignment-free by same-multiset/different-order skeletons and measured by
permutation distance (transpositions, cycle type, inversion count). The research question is explicitly
**mathematical**, on two axes:
- **Intra-language.** Within a single system, what is the mathematical structure of its metatheses? Which
  positions permute, with what cycle types; are the permutations a restricted, recurrent set (a sub-structure of
  $S_k$) rather than arbitrary reorderings; do they compose; is there an algebra of a language's own metathesis?
- **Cross-language.** Compared across the relevant related/contact systems, do metathesis permutation patterns
  recur, mirror, or diverge — the specular inversion (TR↔RT) the consonantal-skeleton view was built to catch —
  and does the *permutation* signal carry system/areal information that the feature-change signal does not?

In short: a **mathematical investigation of metathesis** in its own right — its group-theoretic structure within
a language and its comparison across languages — as a second, order-valued dimension of the operator algebra.

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

## 4b. The wider programme — a general mathematics of linguistic systems

Everything above is framed around *phonological correspondences* because that is where the pilot began. But the
method is not specific to sound change. Its core move is domain-general:

> Represent a linguistic relation or unit as a **difference / feature vector** in a representable space; study the
> **geometry and additive/algebraic structure** of the **observed repertoire** against **explicit null models**,
> including the **generable-but-unattested** region — and keep the theory you later want to test *out* of the
> computation.

Read that way, phonological correspondence is **domain 1 of many**. The same object (repertoire $O$, span
$\langle O\rangle$, occupancy, additive index $C(O)$, holes $\langle O\rangle\setminus O$, distributions
$P(o\mid\cdots)$, matroid/rank invariants, directed layer $T$) transfers to other levels of language, each with
its own representation and its own open data. This is the real reason to build the pilot carefully: it is a
**template**, and mathematically analysing "much more about human language" is the point, not a side-effect.

| domain | the unit / "operator" | the repertoire, and what its geometry asks | data resources |
|---|---|---|---|
| **Phonotactics / syllable structure** | licit sequence / template as a feature string | which templates a language occupies vs the generable-but-unattested (holes in sequence space); dependencies among positions | Lexibank segments, PHOIBLE |
| **Phonological inventories** | segment as a feature vector | the geometry of an inventory; occupancy and gaps in feature space; cross-language inventory repertoires | PHOIBLE |
| **Morphology / paradigms** | an alternation or morphological operation | the repertoire of a grammar's alternations (manual §6.1); paradigm geometry; which operations compose | UniMorph, paradigm datasets |
| **Prosody / tone / stress** | a suprasegmental contrast | tone/stress-system repertoires; occupancy and gaps | tonal typology datasets |
| **Lexical semantics / colexification** | a meaning link (which senses share a form) | the geometry of the colexification network; attested vs generable meaning-pairings; semantic "holes" | CLICS, Concepticon |
| **Word-formation** | a derivation / compounding operator | the algebra of word-building; composition and holes | derivational corpora |
| **Grammar / typology** | a typological feature-vector per language | occupancy of the type space; **dependencies among features = implicational universals** (Greenberg) as our *corank*; unattested type combinations as *holes* | WALS, Grambank |
| **Variation & change over time** | a variant, dated | repertoire drift on documented time; the directed layer $T$ generalised | dated corpora, sociolinguistic data |
| **Multimodal (sign, gesture)** | an articulatory-parameter difference | the same geometry in another modality | sign-language phonology datasets |

Two things carry across every row: the **shared invariants** (rank, occupancy, composition/additivity, holes,
distributional dependence) give a common vocabulary for comparing *different* subsystems; and the **discipline**
(discover-then-contrast, explicit nulls, no imported theory) keeps each honest. The grammar/typology row is
especially striking: **implicational universals are exactly the linear dependencies (corank) of a feature
repertoire, and "impossible" language types are its holes** — the same objects this pilot measures for sound.

Each row is a future programme in its own right (its own data, its own paper). The phonological-correspondence
pilot's job is to prove the template works and to fix the method — so that "the mathematics of linguistic
systems" becomes a portable research practice rather than a single study.

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

---

## Annex A — Where the genealogical signal lives

*This annex records a precise reading of the pilot's central negative result and turns it into a map for
Workstreams 2–3. The claim is easy to misstate, so we state it carefully.*

**The precise claim is not that genealogy is absent from phonology.** It is narrower:

> Genealogy does not appear clearly in the flat *inventory of difference-types*, nor in their additive closure.

Knowing that a family uses the operators $\{voi\}$, $\{cont\}$, $\{cont{+}strid\}$ does not identify its history,
because those same difference-types can arise from articulatory anatomy, from segment inventories, and from the
feature representation. Even after destroying the coderivative relation by permuting concepts ($D_R$), the basic
additive structure remains. The genealogical signal lives at a more structured level — **not in *which*
transformations are possible, but in *how they are systematically distributed* across languages, words,
positions, and contexts.** Concretely, it resides in:

1. **Regular correspondence between concrete languages.** The abstract operator $\Delta(t,d)=\{voi\}$ is general
   phonology; it recurs in unrelated languages. A genealogical fact is not "the difference $t\sim d$ exists" but
   "in a specific set of coderivatives, $t$ in language A corresponds *recurrently* to $d$ in language B, in
   certain positions and contexts." The unit is not $o$ but the tuple $(\ell_i,\ell_j,o,c,p,w)$: language pair,
   operator, context, position, weight. The isolated operator is phonology; the **systematic correspondence
   matrix between determinate languages** is history.

2. **Distribution, not mere existence.** Two families can both use $\{voi\}$ yet differ entirely in *where* — one
   among stops, word-initially, in a few concepts; the other among fricatives, intervocalically, pervasively.
   The type is identical; the distribution $P_{ij}(o)$ is not. The pilot's mutual information between operator
   and branch is small but non-zero (IE 0.14, AN 0.22): knowing the branch reduces uncertainty about which
   operators occur. The signal is in the **frequencies and associations**, not the flat catalogue.

3. **Bundles of correspondences.** A historical law is rarely a lone operator. "Grimm" is a *coordinated bundle*
   over several consonant series, a specific community of languages, certain contexts, a direction. The aggregate
   repertoire flattens this; pooling all IE languages loses which operators are shared specifically by, say,
   Germanic and Italic. Genealogy should surface when a model discovers *jointly* a **set of languages + a bundle
   of operators + recurrent contexts** — precisely the tensor $X_{ijo}$, then $X_{ijoc}$, and its factorization
   (W2).

4. **Direction.** The operator is symmetric, $\Delta(t,s)=\Delta(s,t)$, but history is not: $t\to s \neq s\to t$.
   The current repertoire is an **unoriented shadow of history** — it keeps the *shape* of differences and erases
   the *arrow of time*. The directed object $T=(a,b,c,p,\ell_1,\ell_2,w)$ with $T_{t\to s}\neq T_{s\to t}$
   restores it (W2).

5. **Phonological context.** A regular correspondence $s\sim r$ may be $s\to z\to r$ under conditions; the final
   $s\sim r$ hides the route. Without context, different histories yield the same operator, so the law is a
   *conditional* distribution $P(o\mid c,\ell_i,\ell_j)$ (W2, order-2).

6. **Morphology.** Correspondences that recur in paradigms, declensions, and morpheme boundaries carry
   continuity more sharply than the abstract operator: an alternation confined to a nominal plural or an
   inherited verbal ending is far less likely to be shared by chance than a free-floating segment difference.
   Traditional genealogy leans on phonology *and* lexicon *and* morphology *and* grammar together.

7. **Which words participate.** $\{voi\}$ occurs in thousands of non-historical comparisons; its historical value
   rises when it recurs in the *same* lexical families — numerals, kinship, body parts, basic verbs, pronouns,
   grammatical morphemes. Genealogy lives in the association
   $\text{form}\leftrightarrow\text{meaning}\leftrightarrow\text{systematic correspondence}$. The
   concept-permutation control shows the *general* additive structure survives without semantics, but the
   *concrete* genealogy cannot be reconstructed without knowing which forms belong to which lexical sets.

8. **Emergence from joint structure.** There is no isolated property called "genealogy" inside a phoneme.
   Genealogy is an **emergent property of the systematic covariation of many dimensions** —
   $\text{relational phonology} + \text{lexicon} + \text{morphology} + \text{context} + \text{direction} +
   \text{distribution} + \text{time}$. The genetics analogy is exact: a single base or a single mutation reveals
   no parentage; a *distributed pattern* of thousands of variants does. An isolated operator is a possible
   mutation; a matrix of recurrent, shared, bundled correspondences is descent (and contact, and divergence).

9. **Genealogy vs typology.** Natural transformations (voicing, fricativization, nasalization, palatalization)
   are reusable by any language — that is *typological* signal. What is *genealogical* is the **particular
   configuration of their reuse**: systematic correspondences over concrete word-sets, multiple coordinated
   transformations, shared morphology, shared irregularities, distributions consistent with a history of
   divergence.

10. **The branch case, read correctly.** In IE, branch type-repertoires overlap no more than random groupings —
    the basic types are set by the shared inventory. In AN they *are* more differentiated than chance (more
    distinct inventories/packages per branch). But IE's null-at-the-type-level does **not** mean no genealogy;
    it means genealogy must be sought in the more informative space — edge weights, distributions, pairwise
    correspondences, contexts, direction, lexical series.

**A useful reformulation.** The *repertoire* asks: *what classes of difference does this set of languages use?*
— which yields $O$. *Genealogy* asks: *which language corresponds systematically with which, via what
differences, in what words, positions, contexts, and directions?* — which needs $X_{ijoc}$ and, ultimately, a
temporal dimension. So it is wrong to say genealogy "comes from somewhere other than phonology"; rather:

> Genealogy comes from the historical organization of phonology into a network of **conditioned**
> correspondences, not from the abstract inventory of possible transformations.

$$\boxed{\text{Phonology provides the operations; genealogy is in their pattern of distribution.}}$$

This is exactly why the pilot's honest "representational, not (type-level) genealogical" result is a *doorway*,
not a dead end: it says the genealogical signal is real but lives one level up, in the distributed, directed,
context- and lexicon-conditioned network — the object Workstreams 2 and 3 are built to measure.
