# The Directed, Context-Conditioned Layer of Phonological Correspondences

### Letting sound laws emerge from documented forms — a tensor-and-MDL account (protoform-agnostic)

**Alejandro Toledo Martínez** — Independent researcher (ORCID: 0009-0000-1277-9697)

**Preprint · SKELETON / DRAFT · CC BY 4.0**

**Companion to** *Additive Structure of Phonological Correspondences* (the pilot, "order 0"); this is
**Workstream 2** of the research programme. **Repository:** https://github.com/toledoal/phonological-correspondences

*(This file is a section skeleton, not a finished paper. Each section states what it will contain; `‹stub›`
marks content to be written once the computations land.)*

---

## Abstract  ‹stub›

One paragraph. The pilot studied the *symmetric* repertoire of feature-difference operators and found its
additive geometry to be representational, not (at the type level) genealogical — the genealogical signal living
one level up, in the *distribution* of correspondences across languages, contexts, and direction. This paper
builds that level: a **directed, context-conditioned** model in which recurrent **bundles of correspondences**
and **conditioned rules** are *discovered*, not supplied, and only afterwards contrasted with known sound laws.
State the headline once results exist (which laws emerge; how much genealogy the distribution carries; what
direction can be recovered reconstruction-free). ‹fill after results›

---

## 1. Introduction — from a symmetric shadow to a directed network

- Recap the pilot in two sentences: operator $\Delta(a,b)=\mathbf 1[\phi(a)\neq\phi(b)]$; repertoire $O$; the
  additive structure is representational; **genealogy lives in the distribution** (pilot Annex A). ‹stub›
- The gap this paper closes: a bare operator is general phonology; a *sound law* is a **coordinated, directed,
  context-conditioned bundle over specific languages**. Genealogy is a property of that joint structure. ‹stub›
- The stance is unchanged: **discover first, contrast later.** We do not insert Grimm, Grassmann, Verner, or
  Polynesian lenition; we test whether they *fall out* as compressive structure. ‹stub›
- Contributions (list once written): the order-1 tensor and its bundles; the order-2 conditioned rules via MDL;
  reconstruction-free direction; a historical-holdout evaluation. ‹stub›

## 2. Objects: orders 0, 1, 2, and the directed operator

- **Order 0 (pilot):** the symmetric repertoire $O$ and $C(O)$ — the unoriented shadow. ‹stub›
- **Order 1:** the tensor $X_{ijo}$ = normalized frequency of operator $o$ between languages $i,j$. Captures
  *which languages* share *which operators* and how often. ‹stub›
- **Order 2:** $X_{ijoc}$ — add context $c$ (preceding/following segment, position, stress, morphological
  boundary). The conditional $P(o\mid c,\ell_i,\ell_j)$ is the object a sound law actually is. ‹stub›
- **The directed operator:** $T=(a,b,c,p,\ell_1,\ell_2,w)$ with signature $\sigma(T)=\Delta(a,b)$ but
  $T_{a\to b}\neq T_{b\to a}$. Define precisely; relate to $X_{ijoc}$. ‹stub›

## 3. Data and method

- **Corpora:** Lexibank (IPA-segmented), IE-CoR; dated/attested stages for the time signal (documented dates,
  not reconstructed ancestors). ‹stub›
- **Building the tensors:** coderivative sets (statistical, as in the pilot) → aligned correspondences tagged by
  language pair, position, and context → $X_{ijo}$, $X_{ijoc}$. ‹stub›
- **Bundle discovery (order 1):** non-negative tensor factorization $X\approx\sum_q\lambda_q\,a_q\otimes a_q
  \otimes b_q$ — each component = a set of languages ($a_q$) × a bundle of operators ($b_q$). Model selection
  for the number of components. ‹stub›
- **Rule discovery (order 2):** Minimum Description Length — a context-conditioned set of operators earns the
  name *rule* when it minimizes $L(\mathcal R)+L(D\mid\mathcal R)$; define the code precisely. ‹stub›
- **Direction without reconstruction:** enumerate the admissible sources of an arrow that do *not* import a
  reconstructed ancestor — documented dates $t$; distributional/tensor asymmetry; markedness-neutral cues — and
  state honestly what direction can and cannot be recovered. ‹stub›
- **Nulls & controls:** the pilot's discipline extended to the tensor (concept-permuted $D_R$; language-grouping
  null; language-level bootstrap of components). ‹stub›

## 4. Results I — emergent bundles (order 1)

- The NMF components of $X_{ijo}$: report the top components (language-set × operator-bundle). ‹fill›
- Contrast (post hoc, not input): do components align with known subgroups / law-bundles? Report agreement
  (adjusted Rand / NMI) — *after* discovery. ‹fill›
- Honest read: which bundles are genealogical, which areal/typological, which artifactual. ‹fill›

## 5. Results II — context-conditioned rules (order 2) and emergent laws

- $P(o\mid c,\ell_i,\ell_j)$ and the MDL rule set. ‹fill›
- **The test:** do known laws (Grimm, Grassmann, Verner, Polynesian lenition, rhotacism) emerge as compressive,
  context-conditioned bundles *without being supplied*? Success criterion and **falsifier** (no component/rule
  beats chance against the known-law inventory). ‹fill›
- Worked emergent rule(s) in real words. ‹fill›

## 6. Direction — the arrow of time without reconstruction

- What the directed layer recovers from documented time and from asymmetry; what stays undecidable. ‹fill›
- The repertoire as an *unoriented shadow*; how much orientation the data restore. ‹fill›

## 7. Historical-holdout evaluation

- Blind discovery (no laws, no trees, in some runs no family labels) → external contrast (laws, reconstructions,
  chronologies, contact). Metrics: ARI, NMI, law-recovery rate. Non-match as diagnosis. ‹fill›

## 8. Discussion

- Genealogy realized as distributional structure (the pilot's Annex A, now measured). ‹stub›
- Relation to phylogenetic-network work (Nelson-Sathi et al.; François linkages): we discover bundles rather than
  add borrowing edges to a tree. ‹stub›
- What "emergent law" means, and its limits. ‹stub›

## 9. Limitations and scope  ‹stub›

Tensor sparsity and rank selection; context coding choices; direction is partial; still corpus/aligner-dependent;
pilot families only unless W1 has scaled. Everything beyond stays in the research programme.

## 10. Reproducibility  ‹stub›

New `make` targets (tensor build, NMF, MDL, direction, holdout); datasets and versions; seeds; durable results
store (`data/results/`).

## References  ‹stub›

Reuse the pilot's [1]–[22]; add: non-negative tensor factorization; Minimum Description Length (Rissanen;
Grünwald); sound-change typology for the *contrast* set (Kümmel); any tensor-linguistics precedents.
