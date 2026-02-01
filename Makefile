# Training Parser Makefile
# ANTLR jar is automatically downloaded when needed (checks if exists first)

ANTLR_JAR := antlr-4.9.3-complete.jar
ANTLR_URL := https://www.antlr.org/download/antlr-4.9.3-complete.jar

include makefiles/virtualenvironment.mk

install: install-githooks install-antlr
	@echo "Installation complete"
.PHONY: install

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

$(ANTLR_JAR):
	@if [ ! -f $(ANTLR_JAR) ]; then \
		echo "Downloading ANTLR 4.9.3..."; \
		if command -v curl > /dev/null; then \
			curl -L -O $(ANTLR_URL); \
		elif command -v wget > /dev/null; then \
			wget $(ANTLR_URL); \
		else \
			echo "Error: No download tool found (curl or wget)"; \
			exit 1; \
		fi; \
	else \
		echo "ANTLR jar already exists: $(ANTLR_JAR)"; \
	fi

install-antlr: $(ANTLR_JAR)
.PHONY: install-antlr

test: check-virtual-env
	${MAKE} typecheck
	${MAKE} compile-grammar
	${MAKE} test-python
	${MAKE} validate-datasets
	${MAKE} test-json-export
.PHONY: test

validate-datasets:
	${MAKE} validate-bench-centric
	${MAKE} validate-set-centric
.PHONY: validate-datasets

validate-set-centric: check-virtual-env
	python3 validate_set_centric.py
.PHONY: validate-set-centric

validate-bench-centric: check-virtual-env
	python3 validate_bench_centric.py
.PHONY: validate-bench-centric

test-json-export: check-virtual-env
	@echo "Testing JSON export from training data..."
	python3 main_export.py training-sample_initial.txt -o .test-output.json
	@if [ -f .test-output.json ]; then \
		rm .test-output.json; \
	else \
		echo "✗ JSON export or validation failed"; \
		exit 1; \
	fi
.PHONY: test-json-export

test-python: check-virtual-env
	pytest parser tests
.PHONY: test-python

typecheck: check-virtual-env
	uv run mypy --strict parser --exclude venv --exclude .venv
.PHONY: typecheck

pre-commit: test
.PHONY: pre-commit

compile-grammar: training.g4 $(ANTLR_JAR)
	rm -rf dist/
	java -jar $(ANTLR_JAR) -Dlanguage=Python3 training.g4 -listener -visitor -o dist
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

output.json: check-virtual-env data.txt
	FILE=data.txt $(MAKE) output.json-generic
.PHONY: output.json

output.json-generic: check-virtual-env
	python3 parse_to_json.py $(FILE) --output output.json
.PHONY: output.json-generic

compact: check-virtual-env output.json
	python3 compact_from_json.py output.json
.PHONY: compact

compact-generic: check-virtual-env
	python3 compact_from_json.py $(FILE)
.PHONY: compact-generic
