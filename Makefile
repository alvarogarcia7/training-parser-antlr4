virtualenvironment:
	python3 -m venv venv
.PHONY: virtualenvironment

install: requirements install-githooks
.PHONY: install

install-githooks:
	pre-commit install
.PHONY: install-githooks

test:
	$(MAKE) typecheck
.PHONY: test

typecheck:
	echo "mypy still not configured"
.PHONY: typecheck

requirements:
	pip3 install -r requirements.txt
.PHONY: requirements

pre-commit: test
.PHONY: pre-commit
