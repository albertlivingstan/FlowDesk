PYTHON ?= python3.11
VENV_PYTHON := .venv/bin/python

.PHONY: install run demo test validate poller reviews

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -r automation/requirements-dev.txt

run:
	$(VENV_PYTHON) -m uvicorn automation.main:app --host 127.0.0.1 --port 8000

demo:
	DRY_RUN=true $(VENV_PYTHON) -m uvicorn automation.main:app --host 127.0.0.1 --port 8000

test:
	$(VENV_PYTHON) -m pytest -q

validate:
	$(VENV_PYTHON) -m automation.validate_project

poller:
	$(VENV_PYTHON) -m automation.poller

reviews:
	$(VENV_PYTHON) -m automation.poller --list-reviews
