.PHONY: clean clean-test clean-pyc clean-build help
.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python3 -c "$$BROWSER_PYSCRIPT"

help:
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install: clean ## install dependencies
	poetry install

lint: ## check style with flake8
	poetry run flake8

test: ## run pytests
	poetry run pytest

coverage: ## generate code coverage results
	poetry run pytest --cov --cov-report html

coverage-view: ## open code coverage results in a browser
	make coverage || true
	$(BROWSER) htmlcov/index.html

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

docker-build: ## Build a docker container for development and testing
	docker build -t map-engraver:v1 .

docker-it: ## Run a docker container in interactive mode.
	docker run -it --rm \
	-v `pwd`:/usr/src/map-engraver \
	-w /usr/src/map-engraver \
	map-engraver:v1
