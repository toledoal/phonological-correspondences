# Additive Structure of Phonological Correspondences â reproducible pipeline
# Usage: make <target> FAMILY="Indo-European"   (or FAMILY="Austronesian")
VENV=./.venv/bin/python
FAMILY?=Indo-European
.PHONY: help venv family algebra universes nulls additive repr-control superposition \
        cognate-eval distributions regimes chains patterns sensitivity figures paper manual clean

help:                                        ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'

venv:                                        ## create venv and install deps (panphon, lingpy, networkx, â¦)
	python3.12 -m venv .venv && ./.venv/bin/pip install -q -r requirements.txt

# ---- analyses on the bundled repertoire data/db/transf.db (no corpora needed) ----
algebra:                                     ## atoms, rank/corank, XOR-break, C(O)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) algebra.py
universes:                                   ## three universes and occupancies + C_Omega
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) universes.py
nulls:                                       ## six nested null models for C(O) + bootstrap
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) nulls.py
additive:                                    ## additive combinatorics (tau, kappa, energy), circuits, holes
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) additive.py
repr-control:                                ## representation-induced structure control (O vs U_S)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) repr_control.py
sensitivity:                                 ## sweep support threshold, weight cap, feature subset (invariance)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) sensitivity.py
chains:                                      ## preferred change corridors (monotone dimensions)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) chains.py
patterns:                                    ## operators, emergent classes, hubs (intra-system)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) patterns.py

# ---- analyses that need the corpora (see data/lexicon/README.md) ----
family:                                      ## build the repertoire from Lexibank (writes data/db/transf.db)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) lexibank_corr.py
superposition:                               ## branch decomposition + grouping null (needs corpora + glottolog)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) branch_algebra.py
distributions:                               ## P_L(o), entropy, N_eff, mutual information (needs corpora)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) distributions.py
independent-omega:                           ## alignment-free opportunity (bounds Ω_D circularity; needs corpora)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) independent_omega.py
bootstrap-lang:                              ## language-level bootstrap of C(O) (valid unit; needs corpora, slow)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) bootstrap_lang.py
cognate-eval:                                ## LexStat vs IE-CoR expert cognacy (needs iecor)
	cd src && ../$(VENV) cognate_eval.py
regimes:                                     ## four corpus regimes D_G/D_L/D_C/D_R (needs iecor)
	cd src && ../$(VENV) regimes.py
figures:                                     ## regenerate G_S, G_O, G_L figures (G_L needs corpora)
	cd src && for pair in "Indo-European:ie" "Austronesian:an"; do \
	  F=$${pair%%:*}; s=$${pair##*:}; \
	  TF_FAMILY="$$F" ../$(VENV) fig_graph.py    > ../docs/manual/fig-graph-$$s.tex; \
	  TF_FAMILY="$$F" ../$(VENV) fig_opgraph.py  > ../docs/manual/fig-opgraph-$$s.tex; \
	  TF_FAMILY="$$F" ../$(VENV) fig_langgraph.py> ../docs/manual/fig-langgraph-$$s.tex; \
	done

# ---- documents (need xelatex) ----
paper:                                        ## build the paper PDF (docs/paper.en.pdf)
	bash docs/build-paper.sh
manual:                                       ## build the manual PDF (docs/manual/BOOK.en.pdf)
	bash docs/manual/build.sh

clean:                                        ## remove the generated repertoire (bundled copy stays in git)
	rm -f data/db/transf.db
