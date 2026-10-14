PYTHON       := python3
VENV         := .venv
VENV_PYTHON  := $(VENV)/bin/python
VENV_PIP     := $(VENV)/bin/pip
VENV_FLAKE8  := $(VENV)/bin/flake8
VENV_MYPY    := $(VENV)/bin/mypy

APP          := a_maze_ing.py
CONFIG       ?= config.txt
WHL          := dist/mazegen-1.0.0-py3-none-any.whl

MYPY_FLAGS   := --warn-return-any \
                --warn-unused-ignores \
                --ignore-missing-imports \
                --disallow-untyped-defs \
                --check-untyped-defs

.PHONY: all install run debug clean fclean lint lint-strict test build help


all: help


$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip


install: $(VENV)
	$(VENV_PIP) install flake8 mypy pytest build


build: install
	$(VENV_PYTHON) -m build
	$(VENV_PIP) install --force-reinstall $(WHL)


run: install
	$(VENV_PYTHON) $(APP) $(CONFIG)

debug: install
	$(VENV_PYTHON) -m pdb $(APP) $(CONFIG)


lint: install
	$(VENV_FLAKE8) .
	$(VENV_MYPY) . $(MYPY_FLAGS)

lint-strict: install
	$(VENV_FLAKE8) .
	$(VENV_MYPY) . --strict


test: install
	$(VENV_PYTHON) -m pytest -v


clean:
	$(VENV_PYTHON) -c "import shutil, pathlib; \
[shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; \
[shutil.rmtree(p, ignore_errors=True) for p in ['.mypy_cache', '.pytest_cache', 'build', 'dist']]"

fclean: clean
	rm -rf $(VENV)


help:
	@echo "Comandos disponíveis:"
	@echo "  make install       → cria .venv e instala dependências de dev"
	@echo "  make build         → gera .whl/.tar.gz e instala o pacote"
	@echo "  make run           → executa o programa (CONFIG=config.txt)"
	@echo "  make debug         → executa no pdb"
	@echo "  make lint          → flake8 . + mypy . (flags obrigatórias)"
	@echo "  make lint-strict   → flake8 . + mypy . --strict"
	@echo "  make test          → pytest"
	@echo "  make clean         → remove caches/build"
	@echo "  make fclean        → clean + remove .venv"
