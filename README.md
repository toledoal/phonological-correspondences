# Additive Structure of Phonological Correspondences

A protoform-agnostic method for discovering mathematical patterns in documented linguistic systems.

**Author:** Alejandro Toledo Martínez — Independent researcher
([ORCID 0009-0000-1277-9697](https://orcid.org/0009-0000-1277-9697))
**Status:** preprint / pilot study · **License:** code MIT, documents CC BY 4.0

---

## What this is

Instead of reconstructing an ancestor and deriving documented forms from it, this project **inverts the order of
inference**: it describes each attested sound correspondence as the *set of phonological features that differ*
between two aligned segments — a symmetric **operator** — turning a language family into a measurable
**repertoire** of feature-difference vectors, computed with **no reconstruction, no sound laws, and no externally
imposed sound classes**. History is brought back only *afterward*, as an independent test.

Two documents accompany the code:

- **`docs/paper.en.pdf`** — the paper (the thesis and the null-controlled results).
- **`docs/manual/BOOK.en.pdf`** — the manual: a didactic, worked-example treatment (start with **Chapter 0**).

## Headline results (Indo-European & Austronesian pilots)

- **Occupancy is not sparsity of languages but vastness of the space.** Of the differences the corpus actually
  makes available, IE realizes 63% and AN 48%.
- **The repertoire is additively organized** — composing two operators lands back in the repertoire far more
  often than chance, surviving six nested null models up to sampling from the corpus's own opportunity set.
- **That additive structure is representational, not genealogical** (a concept-permuted control matches it).
- **The generable-but-unattested operators** form a concrete geometry of near-misses.

## Install

```bash
python3.12 -m venv .venv
./.venv/bin/pip install -r requirements.txt
# or:  make venv
```

Main dependencies: `panphon`, `lingpy`, `networkx` (see `requirements.txt`). Building the PDFs additionally needs
`xelatex` (TeX Live / MacTeX).

## Reproduce

The repertoire `data/db/transf.db` is **bundled**, so the geometry / additive / null analyses run immediately,
with no large downloads:

```bash
make algebra      FAMILY="Indo-European"     # atoms, rank/corank, XOR-break, C(O)
make universes    FAMILY="Indo-European"     # three universes, three occupancies, C_Omega
make nulls        FAMILY="Indo-European"     # six nested null models for C(O) + bootstrap
make additive     FAMILY="Indo-European"     # tau, kappa, energy; matroid circuits; hole geometry
make repr-control FAMILY="Austronesian"      # representation-induced structure control
make chains       FAMILY="Indo-European"     # preferred change corridors
make patterns     FAMILY="Indo-European"     # operators, emergent classes, hubs
```

Swap `FAMILY="Austronesian"` freely. `make help` lists every target.

The targets that **rebuild the repertoire or need branch/cognacy data** require the corpora — see
[`data/lexicon/README.md`](data/lexicon/README.md) for how to obtain them (Lexibank, IE-CoR). These are
`make family`, `superposition`, `distributions`, `cognate-eval`, `regimes`, `figures`.

Build the documents:

```bash
make paper     # -> docs/paper.en.pdf
make manual    # -> docs/manual/BOOK.en.pdf
```

## Layout

```
src/            the analysis pipeline (one script per measure)
docs/           paper (paper.en.*), manual (manual/BOOK.en.*), build scripts, figures, md2tex.py
data/db/        transf.db — the bundled correspondence repertoire (derived, redistributable)
data/*.csv      cached Glottolog classification (branch labels)
data/lexicon/   where the corpora go (not bundled; see its README)
```

## Data & licensing of inputs

The **bundled** files are derived/redistributable: `data/db/transf.db` (feature-difference counts, no verbatim
corpus) and the Glottolog classification caches (CC BY 4.0, © Glottolog). The **corpora themselves** (Lexibank,
IE-CoR) are **not** included; download them under their own licenses as described in `data/lexicon/README.md`.

## How to cite

Toledo Martínez, A. (2026). *Additive Structure of Phonological Correspondences: A protoform-agnostic method for
discovering mathematical patterns in documented linguistic systems.* Preprint. (See `CITATION.cff`.)

## License

- **Code** (`src/`, `docs/*.sh`, `docs/md2tex.py`, `Makefile`): MIT — see [`LICENSE`](LICENSE).
- **Documents & figures** (`docs/paper.en.*`, `docs/manual/*`): CC BY 4.0 — see [`LICENSE-docs.txt`](LICENSE-docs.txt).
