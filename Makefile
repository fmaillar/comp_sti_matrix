# Makefile pour exécuter l'analyse depuis src/core/main.py

.PHONY: run clean test

CONFIG ?= data/GE_H2/sti_config.yaml

# Exécution du script principal (via -m pour respecter les imports)
run:
	python -m comp_sti_matrix.cli.run_analysis --config $(CONFIG)

# Nettoyage des fichiers pycache
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + || true

# Lancer les tests si tu les mets en place
test:
	pytest comp_sti_matrix/tests/

