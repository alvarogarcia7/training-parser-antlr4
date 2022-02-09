virtualenvironment:
	python3 -m venv venv
.PHONY: virtualenvironment

install: requirements install-githooks install-antlr
.PHONY: install

install-githooks:
	pre-commit install
.PHONY: install-githooks

install-antlr:
	curl -O https://www.antlr.org/download/antlr-4.9.3-complete.jar

test: typecheck
.PHONY: test

typecheck:
	mypy . --exclude venv --strict --warn-unreachable --warn-return-any --disallow-untyped-calls
.PHONY: typecheck

requirements: requirements.txt
	pip3 install -r requirements.txt

pre-commit: test
.PHONY: pre-commit

compile-grammar: training.g4
	time java -jar antlr*.jar -Dlanguage=Python3 training.g4 -listener -visitor -o dist
