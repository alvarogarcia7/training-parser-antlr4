virtualenvironment:
	python3 -m venv venv
.PHONY: virtualenvironment

check-virtual-env:
	@# Test if the variable is set
	@if [ -z "${VIRTUAL_ENV}" ]; then                                               \
  		echo "Need to activate virtual environment: source ./venv/bin/activate";    \
  		false;       																\
  	fi

install: requirements install-githooks install-antlr
.PHONY: install

install-githooks:
	pre-commit install
.PHONY: install-githooks

install-antlr:
	curl -O https://www.antlr.org/download/antlr-4.9.3-complete.jar

test: typecheck compile-grammar test-python
.PHONY: test

test-python: check-virtual-env
	pytest parser tests
.PHONY: test-python

typecheck:
	mypy . --exclude venv
.PHONY: typecheck

requirements: requirements.txt
	pip3 install -r requirements.txt

pre-commit: test
.PHONY: pre-commit

compile-grammar: training.g4
	rm -rf dist/
	java -jar antlr*.jar -Dlanguage=Python3 training.g4 -listener -visitor -o dist
	@echo "Grammar generated"

run: check-virtual-env
	$(MAKE) run-splitter
	$(MAKE) to-clipboard
.PHONY: run

run-splitter:
	# paste data into data.txt
	# If data is coming from todoist, it is compacted into a single line, separated by ' - ' symbols. Split again using:
	# %s/ - /\r/g
	python3 splitter.py
	cat output.csv | pbcopy
.PHONY: run-splitter

to-clipboard:
	@cat output.csv | pbcopy
	@echo "The output is in your copy-paste clipboard."
	@echo "Paste it in column Strength!F"
.PHONY: to-clipboard
