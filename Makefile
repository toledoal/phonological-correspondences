# transformations â teorÃ­a algebraica del cambio lingÃ¼Ã­stico
VENV=./.venv/bin/python
FAMILY?=Indo-European
.PHONY: all venv operators clean
all: operators super g2p cross                               ## pipeline (por ahora X3)
venv:                                        ## crea el venv (panphon + stack cientÃ­fico)
	python3.12 -m venv .venv && ./.venv/bin/pip install -q -r requirements.txt
super:                                       ## X-super Â· reconstrucciones PIE como superposiciones (entropÃ­a)
	$(VENV) src/pie_super.py
g2p:                                         ## X1 nativo Â· correspondencias multi-rama (epitran G2P + alineamiento)
	$(VENV) src/correspond.py
residue:                                     ## RESIDUO Â· asociaciÃ³n conceptoâsegmento entre familias (tercer registro)
	$(VENV) src/residue.py
family:                                      ## estudiar UNA familia intra-sistema: make family FAMILY="Austronesian"
	TF_FAMILY="$(FAMILY)" $(VENV) src/lexibank_corr.py
	TF_FAMILY="$(FAMILY)" $(VENV) src/patterns.py
algebra:                                     ## X4 Â· Ã¡lgebra de operadores intra-sistema (XOR, Ã¡tomos, cierre)
	TF_FAMILY="$(FAMILY)" $(VENV) src/algebra.py
chains:                                      ## X4 Â· cadenas preferentes (corredores de cambio monÃ³tonos)
	TF_FAMILY="$(FAMILY)" $(VENV) src/chains.py
branches:                                    ## ramas (subgrupos) de una familia vÃ­a Glottolog: make branches FAMILY="Austronesian"
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) branches.py
superposition:                               ## FASE2 Â· Â¿el Ã¡lgebra de la familia es superposiciÃ³n de Ã¡lgebras de rama?
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) branch_algebra.py
cognate-eval:                                ## FASE2 Â· D_cognado vs D_conceptual: Â¿cuÃ¡nto contamina LexStat? (IE-CoR gold)
	$(VENV) src/cognate_eval.py
repr-control:                                ## V4-6 - control de estructura inducida por la representacion (O_L vs U_S)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) repr_control.py
universes:                                   ## V4-2/3 - universos U_S / Omega_D y tres ocupaciones + C_Omega
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) universes.py
nulls:                                       ## V4-4 - jerarquia de nulos 0-5 para C(O) con p_MC + bootstrap
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) nulls.py
additive:                                    ## V4-5 - combinatoria aditiva (tau,kappa,E), circuitos, huecos
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) additive.py
patterns:                                    ## X4 Â· patrones matemÃ¡ticos DENTRO de un sistema (operadores, clases, ejes)
	$(VENV) src/patterns.py
cross:                                        ## X5-cross Â· operadores que recurren entre ramas independientes
	$(VENV) src/cross.py
operators:                                   ## X3 Â· descubrir operadores desde coderiv â data/db/transf.db
	$(VENV) src/operators.py
clean:
	rm -f data/db/transf.db
distributions:                               ## V4-7 - P_L(o), entropia, N_eff, info mutua O x rama/concepto/contexto
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) distributions.py
regimes:                                     ## V4-8 - cuatro regimenes D_G/D_L/D_C/D_R + prestamos (IE-CoR)
	$(VENV) src/regimes.py
manual:                                      ## Fase 4 - compila el MANUAL (docs/manual/BOOK.en.md -> PDF)
	bash docs/manual/build.sh
figures:                                     ## regenera las figuras del manual (G_S, G_O, G_L para IE y AN)
	cd src && for F in "Indo-European" "Austronesian"; do \
	  s=$$(echo $$F | cut -c1-2 | tr A-Z a-z); \
	  TF_FAMILY="$$F" ../$(VENV) fig_graph.py    > ../docs/manual/fig-graph-$$s.tex; \
	  TF_FAMILY="$$F" ../$(VENV) fig_opgraph.py  > ../docs/manual/fig-opgraph-$$s.tex; \
	  TF_FAMILY="$$F" ../$(VENV) fig_langgraph.py> ../docs/manual/fig-langgraph-$$s.tex; \
	done
paper:                                       ## compila el PAPER version-tesis (docs/paper.en.md -> PDF)
	bash docs/build-paper.sh
sensitivity:                                 ## FASE1 - sensibilidad: barre umbral, cap de peso y rasgos (bundled)
	cd src && TF_FAMILY="$(FAMILY)" ../$(VENV) sensitivity.py
