
PYTHON      := python3
MAIN        := a_maze_ing.py
CONFIG      := config.txt
PIP         := $(PYTHON) -m pip
SRC         := mazegen/ a_maze_ing.py

MYPY_FLAGS  := --warn-return-any \
               --warn-unused-ignores \
               --ignore-missing-imports \
               --disallow-untyped-defs \
               --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test build help


	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy pytest build


run:
	$(PYTHON) $(MAIN) $(CONFIG)


debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true

lint:
	flake8 .
	mypy . $(MYPY_FLAGS)

lint-strict:
	flake8 .
	mypy . --strict

test:
	$(PYTHON) -m pytest -v

build:
	$(PYTHON) -m build

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       → instala dependências"
	@echo "  make run           → executa o programa"
	@echo "  make debug         → executa no pdb"
	@echo "  make clean         → limpa caches e builds"
	@echo "  make lint          → flake8 + mypy (flags obrigatórias)"
	@echo "  make lint-strict   → flake8 + mypy --strict"
	@echo "  make test          → roda pytest"
	@echo "  make build         → gera .whl e .tar.gz"
