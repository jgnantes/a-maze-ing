VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
CONFIG = config.txt

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy

run: install
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug: install
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

build: install
	$(PIP) install build
	$(PYTHON) -m build

clean:
	rm -rf __pycache__ .mypy_cache *.pyc $(VENV) build dist *.egg-info

lint: install
	$(PYTHON) -m flake8 . --exclude=.venv
	$(PYTHON) -m mypy . --exclude .venv --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs