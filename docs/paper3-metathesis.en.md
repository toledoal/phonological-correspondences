# The Permutation Dimension: A Mathematics of Metathesis

### Modelling reordering as an operator on the consonantal skeleton (protoform-agnostic)

**Alejandro Toledo Martínez** — Independent researcher (ORCID: 0009-0000-1277-9697)

**Preprint · SKELETON / DRAFT · CC BY 4.0**

**Companion to** *Additive Structure of Phonological Correspondences* (the pilot); this is a distinct dimension of
the same programme (research programme W7, promoted to its own paper). **Repository:**
https://github.com/toledoal/phonological-correspondences

*(Section skeleton, not a finished paper. `‹stub›`/`‹fill›` mark content to be written once the computations
land. The central open decision — the right mathematical object for a metathesis "event" — is laid out in §2 as a
menu to settle, not yet fixed.)*

---

## Abstract  ‹stub›

The pilot's operator $\Delta(a,b)$ lives in feature space $\mathbb F_2^n$ *at a fixed slot*; by construction it
cannot represent a **reordering** of segments (the monotonic aligner mis-scores metathesis as substitutions and
gaps). This paper adds the orthogonal dimension: metathesis as a **permutation of the consonantal skeleton's
positions**. It (i) fixes a mathematical object for the metathesis event, (ii) builds an alignment-free detector,
(iii) measures the intra-language algebra of a system's reorderings and (iv) compares it across systems. State the
headline once results exist. ‹fill›

---

## 1. Introduction — the axis the feature operator cannot see

- Recap: the pilot operator is a feature-difference *at aligned slots*; alignment is monotonic (order-preserving),
  so reordering is invisible and leaks as noise. ‹stub›
- Metathesis is common and famous (Spanish *murciélago* ← *murciégalo*; *cocodrilo* ← *crocodilo*; *palabra* ←
  *parabola*; *milagro*, *peligro*): from **adjacent swaps** to **long-distance moves**. ‹stub›
- Thesis: metathesis is a **second, orthogonal dimension** of the change operator — order, not features — and it
  has its own measurable algebra, within a language and across languages. Discover-then-contrast, as always. ‹stub›

## 2. The object — what mathematical event models a metathesis? *(the central design question)*

A menu of candidate formalisms, from simplest to richest; the paper selects and justifies one (or a layered set).

- **(A) Permutation $\pi\in S_k$** of the skeleton's positions — the object; its **action** on the order is the
  *event*. Two coderivatives with the same consonant multiset but different order differ by $\pi$. Brings for
  free: composition (group), **cycle type**, **parity/sign**, **inversion count**, and whether a language is
  restricted to **adjacent transpositions** (Coxeter generators of $S_k$). ‹stub›
- **(B) The full operator $(\pi,\Delta)\in S_k\times\mathbb F_2^n$** — reorder *and* change features together. The
  pilot's operator is the $\pi=\mathrm{id}$ face; metathesis is $\pi\neq\mathrm{id}$. This is the honest event,
  since real metathesis usually co-occurs with feature change. ‹stub›
- **(C) Rearrangement distance** (genome-rearrangement mathematics; Bafna–Pevzner): the event is a sorting
  operation (transposition / reversal / block-move); the **distance** between two skeletons is the minimum number
  of such operations. Handles adjacent swaps (*murciélago*, 1 transposition) and long moves (*cocodrilo*, 1
  block-move) on the same scale, and resonates with the genetics analogy the programme already uses. ‹stub›
- **(D) Braid / crossing view** — if we track *how* segments cross rather than only the endpoint permutation.
  Likely more than needed at first; noted for completeness. ‹stub›
- **Recommendation to argue:** core object $\pi\in S_k$; honest operator $(\pi,\Delta)$; magnitude via
  rearrangement distance. ‹settle›

## 3. Detecting metathesis without reconstruction (and without a monotonic aligner)

- **Alignment-free detector:** for each coderivative pair, compare the consonantal *skeletons*; a **same
  multiset, different order** pair is a metathesis candidate. No NW, no protoform. ‹stub›
- Measure the reordering: the permutation $\pi$ relating the two orders (and its rearrangement distance);
  co-occurring $\Delta$ recorded separately. ‹stub›
- Nulls/controls: chance rate of same-multiset/different-order under a segment-shuffling null; the pilot's
  discipline carried over (concept-permuted $D_R$, language-level resampling). ‹stub›

## 4. Results I — the intra-language algebra of metathesis

- For each language/system: the **set of $\pi$'s** it uses — is it a restricted sub-structure of $S_k$? Only
  adjacent transpositions? Particular cycle types? Do they **compose** (a sub-monoid)? ‹fill›
- Distribution of rearrangement distance; which positions/segments move most. ‹fill›

## 5. Results II — metathesis across languages

- Do the same $\pi$ patterns **recur** across related/contact systems? Is there **specular inversion** (the
  TR↔RT case the consonantal-skeleton view was built to catch)? ‹fill›
- Does the *permutation* signal carry system/areal information the feature-change signal does not (contrast with
  the pilot's distributions)? ‹fill›

## 6. Discussion  ‹stub›

The order dimension beside the feature dimension: the operator algebra as $\mathbb F_2^n \times S_k$; connection
to genome rearrangement; what metathesis adds to "where genealogy lives" (pilot Annex A).

## 7. Limitations and scope  ‹stub›

Skeleton extraction and multiset equality are approximations; partial metathesis co-occurring with deletion is
hard; direction of the reordering (which order is earlier) needs the same reconstruction-free caution as Paper 2.

## 8. Reproducibility  ‹stub›

New `make` targets (metathesis detector, permutation/rearrangement measures); durable results in `data/results/`.

## References  ‹stub›

Reuse the pilot's; add: symmetric-group / Coxeter basics; genome-rearrangement (Bafna & Pevzner; Hannenhalli &
Pevzner); metathesis typology (e.g. Blevins & Garrett) for the *contrast* set.
