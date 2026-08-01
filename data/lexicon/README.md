# Corpora (not bundled)

The large input corpora are **not** included in this repository (they are ~400 MB and carry their own licenses).
Most analyses do **not** need them: the derived repertoire `../db/transf.db` is bundled, so everything under
`make algebra / universes / nulls / additive / repr-control / chains / patterns` runs out of the box.

You only need the corpora to **rebuild** the repertoire or to run branch / cognacy / distribution / figure
targets (`make family / superposition / distributions / cognate-eval / regimes / figures`).

## What to place here

```
data/lexicon/lexibank/     # Lexibank aggregation, CLDF-style, with languages.csv and forms.csv (IPA Segments)
data/lexicon/iecor/        # IE-CoR export with forms.json, cognate_sets.json, languages.json (expert cognacy)
```

The scripts read, from `lexibank/`, the files `languages.csv` (needs `ID, Name, Family, Glottocode`) and
`forms.csv` (needs `Language_ID, Parameter_ID, Segments`); and from `iecor/`, the JSON files listed above.

## Where to get them

- **Lexibank** — the analyzed/aggregated Lexibank data. See the Lexibank project
  (https://github.com/lexibank) and its aggregated release; place the CLDF tables so that
  `languages.csv` and `forms.csv` sit directly under `data/lexicon/lexibank/`.
- **IE-CoR (Indo-European Cognate Relationships)** — https://iecor.clld.org ; export the forms, cognate sets,
  and languages as JSON into `data/lexicon/iecor/`.

## Glottolog

Branch labels come from Glottolog's classification, already **cached** in `../glottolog_classification.csv` and
`../glottolog_languages.csv`, so `make superposition` works without extra downloads. To refresh them, re-derive
from the current Glottolog CLDF release (https://github.com/glottolog/glottolog-cldf), `cldf/values.csv`,
parameter `classification`.

Field names or paths differ in your copy? The relevant constants are at the top of the scripts in `../../src/`
(`LEX`, `IEC`).
