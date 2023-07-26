VIRTUALENV = $(shell which python3) -m venv
VENV_DIR = .venv
VENV := $(if $(VIRTUAL_ENV),$(VIRTUAL_ENV),$(VENV_DIR))
PYTHON = $(VENV)/bin/python
REQ_STAMP = $(VENV)/.req_stamp

# editable
export MODULE_PATH=$(shell pwd)/check_airflow

.DEFAULT: help
help:
	@echo "make init"
	@echo "		prepare development environment and create virtualenv"
	@echo "make test"
	@echo "		run lint and unit tests"
	@echo "make lint"
	@echo "		run lint only"
	@echo "make dep"
	@echo "		dump the current pip packages to requirements.txt"
	@echo "make clean"
	@echo "		clean compiled files and the virtual environment"

virtualenv: $(PYTHON) # creates a virtual environment

# one time virtualenv setup
$(PYTHON):
	@$(VIRTUALENV) $(VENV)
	@$(VENV)/bin/pip install --upgrade pip setuptools wheel
	@$(VENV)/bin/pip install ruff coverage twine mypy bumpversion

init: virtualenv $(REQ_STAMP) # will run any time the requirements.txt file has been updated

$(REQ_STAMP): requirements.txt # install all module requirements
	@$(VENV)/bin/pip install -Ur requirements.txt
	@touch $(REQ_STAMP)

lint:
	@$(VENV)/bin/ruff check ${MODULE_PATH}

test: init lint
		@$(VENV)/bin/coverage erase
		@$(VENV)/bin/coverage run --branch -m unittest tests/*.py
		@$(VENV)/bin/coverage report -m
		@$(VENV)/bin/coverage xml -o coverage.xml

pack: init
	@$(VENV)/bin/python setup.py bdist_wheel

clean:
	@rm -rf $(VENV)
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name .coverage -delete
	@rm -rf dist build *.egg-info

.PHONY: init test lint