# =============================
# Makefile pour comp_sti_matrix
# =============================

PYTHON := python
PACKAGE := comp_sti_matrix
CONFIG := data/GE_H2/sti_config.yaml
ENTRY := $(PACKAGE).cli.run_analysis

# Cible par défaut
run:
	$(PYTHON) -m $(ENTRY) --config $(CONFIG)

# Nettoyage
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + || true
	find . -type f -name "*.pyc" -delete || true
	find . -type f -name "*~" -delete || true
	rm -rf build dist *.egg-info

# Lint et formatage avec Ruff
lint:
	ruff check $(PACKAGE) scripts tests

format:
	ruff format $(PACKAGE) scripts tests

# Tests
test:
	$(PYTHON) -m unittest discover -s tests

# Installation locale
install:
	pip install -e .

# Build
build:
	$(PYTHON) -m build

# Aide
help:
	@echo "Cibles disponibles :"
	@echo "  make run       : Exécute l’analyse principale"
	@echo "  make test      : Lance les tests unitaires"
	@echo "  make lint      : Analyse le code avec ruff"
	@echo "  make format    : Formate le code avec ruff"
	@echo "  make clean     : Supprime les fichiers temporaires"
	@echo "  make install   : Installe le paquet en mode dev"
	@echo "  make build     : Construit les artefacts de distribution"
	@echo "  make help      : Affiche cette aide"

