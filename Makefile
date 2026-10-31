
VENV        := .venv
PYTHON      := $(VENV)/bin/python
MAIN        := a_maze_ing.py
CONFIG      := config.txt
PIP         := $(PYTHON) -m pip
DEPS        := $(VENV)/.deps-installed

MYPY_FLAGS  := --warn-return-any \
               --warn-unused-ignores \
               --ignore-missing-imports \
               --disallow-untyped-defs \
               --check-untyped-defs

.PHONY: install run debug clean fclean lint lint-strict test test-analyzer \
        check build help

$(PYTHON):
	python3 -m venv $(VENV)

$(DEPS): requirements.txt | $(PYTHON)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	touch $(DEPS)

install: $(DEPS)


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

fclean: clean
	rm -rf $(VENV)

lint: $(DEPS)
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

lint-strict: $(DEPS)
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

test: $(DEPS)
	$(PYTHON) -m pytest -v

test-analyzer: $(DEPS)
	$(PYTHON) tools/run_analyzer.py

check: test test-analyzer

build: $(DEPS)
	rm -f mazegen-*.whl mazegen-*.tar.gz
	$(PYTHON) -m build --outdir .
	rm -rf build/ mazegen.egg-info/

help:
	@echo "Available targets:"
	@echo "  make install       create .venv and install dependencies"
	@echo "  make run           run the program with $(CONFIG)"
	@echo "  make debug         run the program under pdb"
	@echo "  make clean         remove caches and build artifacts"
	@echo "  make fclean        clean, then remove .venv"
	@echo "  make lint          flake8 + mypy (subject's required flags)"
	@echo "  make lint-strict   flake8 + mypy --strict"
	@echo "  make test          run the test suite with pytest"
	@echo "  make test-analyzer run maze_analyzer on every test config, 50 seeds"
	@echo "  make check         make test + make test-analyzer"
	@echo "  make build         build mazegen-*.whl and mazegen-*.tar.gz at the repo root"
