.DEFAULT_GOAL := help

# AutoEnv
ENV ?= .env
ENV_GEN := $(shell ./.env.gen ${ENV} .env.required)
include ${ENV}
export $(shell sed 's/=.*//' ${ENV})


# AutoDoc
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove all build, test, coverage and Python artifacts
	rm -rf build dist .eggs .cache
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
	rm -rf .tox .coverage htmlcov coverage-reports
	find . -name '*,cover' -exec rm -fr {} +

.PHONY: test
test: ## run tests quickly with py.test
	py.test tests

.PHONY: test-all
test-all: ## run tests on every python version with tox
	tox

install-%:
	pip install -r $*.txt -U

.PHONY: install
install:
	pip install -U .

.PHONY: lint
lint: ## check style with flake8
	flake8 deeptracy

.PHONY: coverage
coverage: ## check code coverage
	py.test --cov=deeptracy tests --cov-fail-under 5

.PHONY: docs
docs: ## generate and shows documentation
	@make -C docs html


.PHONY: run-with-patton
run-with-patton: ## Run the application with patton
	pip freeze
	patton-server -C postgresql://postgres:postgres@localhost:5433/patton serve&
	sleep 10
	./run.sh

.PHONY: run-with-patton-db
run-with-patton-db: ## Run the application with patton and patton-db loaded
	python ./create_patton_db.py
	patton-server -C postgresql://postgres:postgres@localhost:5433/patton init-db
	patton-server -C postgresql://postgres:postgres@localhost:5433/patton serve&
	sleep 10
	./run.sh

.PHONY: run
run: ## launch the application
	./run.sh

.PHONY: at_local
at_local: ## run acceptance tests without environment. You need to start your own environment (for dev)
	LOCAL_BEHAVE=True behave --no-capture --no-capture-stderr tests/acceptance/features

.PHONY: at_only
at_only: ## run acceptance tests without environment, and just features marked as @only (for dev)
	behave --no-capture --no-capture-stderr --tags=only tests/acceptance/features

.PHONY: at
at: ## run acceptance tests in complete docker environment
	docker-compose -f tests/acceptance/docker-compose.yml stop
	docker-compose -f tests/acceptance/docker-compose.yml rm -f
	docker-compose -f tests/acceptance/docker-compose.yml up -d --build
	sleep 10
	behave --no-capture --no-capture-stderr tests/acceptance/features
	docker-compose -f tests/acceptance/docker-compose.yml kill
	docker-compose -f tests/acceptance/docker-compose.yml rm -f
