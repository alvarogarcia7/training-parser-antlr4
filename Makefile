include makefiles/virtualenvironment.mk

install: requirements install-githooks
.PHONY: install

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

install-antlr:
	curl -O https://www.antlr.org/download/antlr-4.9.3-complete.jar

test: check-virtual-env 
	${MAKE} typecheck
	${MAKE} compile-grammar
	${MAKE} test-python
	${MAKE} validate-datasets
.PHONY: test

validate-datasets:
	${MAKE} validate-bench-centric
.PHONY: validate-datasets

validate-bench-centric: check-virtual-env
	python3 validate_bench_centric.py
.PHONY: validate-bench-centric

test-python: check-virtual-env
	pytest parser tests
.PHONY: test-python

typecheck: check-virtual-env
	mypy --strict parser
.PHONY: typecheck

pre-commit: test
.PHONY: pre-commit

compile-grammar: training.g4
	rm -rf dist/
	java -jar antlr*.jar -Dlanguage=Python3 training.g4 -listener -visitor -o dist
	@echo "Grammar generated"

run: check-virtual-env
	FILE=data.txt $(MAKE) output.csv
	$(MAKE) to-clipboard
.PHONY: run

archive-data:
	touch data/$(shell date "+%Y-%m-%d").txt
	cat data.txt >> data/$(shell date "+%Y-%m-%d").txt
	$(MAKE) save-data

save-data:
	$(MAKE) -C ./data save
	echo "" > data.txt
.PHONY: save-data


run-splitter: output.csv

output.csv: check-virtual-env data.txt
	FILE=data.txt $(MAKE) output.csv-generic

output.csv-generic: check-virtual-env
	# paste data into data.txt
	# If data is coming from todoist, it is compacted into a single line, separated by ' - ' symbols. Split again using:
	# %s/ - /\r/g
	python3 splitter.py $(FILE) --output output.csv
.PHONY: output.csv-generic

verify-splitter: check-virtual-env
	FILE=data.txt $(MAKE) verify-splitter-generic
.PHONY: verify-splitter

verify-splitter-generic: check-virtual-env
	python3 splitter.py $(FILE)
	@echo "Data is correct"
.PHONY: verify-splitter-generic

validate-json: check-virtual-env
	python3 json_validator.py $(SCHEMA) $(FILES)
.PHONY: validate-json

to-clipboard:
	@cat output.csv | pbcopy
	@echo "The output is in your copy-paste clipboard."
	@echo "Open https://docs.google.com/spreadsheets/d/1F1a95XZRIBLXj3TqpEZoIEB1-n17O8KYs65kf0s-HqA/edit#gid=1836141740"
	@echo "Paste it in column Strength!F"
.PHONY: to-clipboard
