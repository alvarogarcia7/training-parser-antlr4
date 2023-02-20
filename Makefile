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

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

install-antlr:
	curl -O https://www.antlr.org/download/antlr-4.9.3-complete.jar

test: check-virtual-env typecheck compile-grammar test-python
.PHONY: test

test-python: check-virtual-env
	pytest parser tests
.PHONY: test-python

typecheck: check-virtual-env
	mypy . --exclude venv
.PHONY: typecheck

requirements: check-virtual-env requirements.txt
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

archive-data: run-splitter
	cp data.txt data/$(shell date "+%Y-%m-%d").txt
	$(MAKE) -C ./data save

run-splitter: check-virtual-env
	# paste data into data.txt
	# If data is coming from todoist, it is compacted into a single line, separated by ' - ' symbols. Split again using:
	# %s/ - /\r/g
	python3 splitter.py
	cat output.csv | pbcopy
.PHONY: run-splitter

to-clipboard:
	@cat output.csv | pbcopy
	@echo "The output is in your copy-paste clipboard."
	@echo "Open https://docs.google.com/spreadsheets/d/1F1a95XZRIBLXj3TqpEZoIEB1-n17O8KYs65kf0s-HqA/edit#gid=1836141740"
	@echo "Paste it in column Strength!F"
.PHONY: to-clipboard
