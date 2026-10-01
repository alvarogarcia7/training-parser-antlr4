# This Makefile has been designed to be executed from the top folder, not from the makefiles folder.
# Hence why the include includes the `makefiles` folder.
include makefiles/python_version.mk

check-virtual-env:
	@# Test if the variable is set (created by `uv sync`)
	@if [ -z "${VIRTUAL_ENV}" ]; then                                               \
  		echo "Need to activate virtual environment:";                               \
  		echo "  uv sync && source .venv/bin/activate";                              \
  		false;       																\
  	fi


# uv-specific targets
uv-sync:
	uv sync --all-extras
	@if [ -f bin/download_antlr.py ]; then \
		python3 bin/download_antlr.py; \
	fi
.PHONY: uv-sync
