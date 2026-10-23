
VENV        := .venv
PYTHON      := $(VENV)/bin/python
MAIN        := app.a_maze_ing
CONFIG      := config.txt
PIP         := $(PYTHON) -m pip
SRC         := app/ mazegen/ tests/

MYPY_FLAGS  := --warn-return-any \
               --warn-unused-ignores \
               --ignore-missing-imports \
               --disallow-untyped-defs \
               --check-untyped-defs

.PHONY: install run debug clean fclean lint lint-strict test build help

$(PYTHON):
	python3 -m venv $(VENV)

install: $(PYTHON)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt


run:
	$(PYTHON) -m $(MAIN) $(CONFIG)


debug:
	$(PYTHON) -m pdb -m $(MAIN) $(CONFIG)


clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ 2>/dev/null || true

fclean: clean
	rm -rf $(VENV)

lint:
	$(PYTHON) -m flake8 $(SRC)
	$(PYTHON) -m mypy $(SRC) $(MYPY_FLAGS)

lint-strict:
	$(PYTHON) -m flake8 $(SRC)
	$(PYTHON) -m mypy $(SRC) --strict

test:
	$(PYTHON) -m pytest -v

build:
	$(PYTHON) -m build

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       → cria o .venv e instala dependências"
	@echo "  make run           → executa o programa"
	@echo "  make debug         → executa no pdb"
	@echo "  make clean         → limpa caches e builds"
	@echo "  make fclean        → clean + apaga o .venv"
	@echo "  make lint          → flake8 + mypy (flags obrigatórias)"
	@echo "  make lint-strict   → flake8 + mypy --strict"
	@echo "  make test          → roda pytest"
	@echo "  make build         → gera .whl e .tar.gz"
