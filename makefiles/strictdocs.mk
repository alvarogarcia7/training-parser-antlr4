# ==============================================================================
# StrictDoc Targets
# ==============================================================================
# This makefile module provides targets for managing StrictDoc requirements
# documentation. StrictDoc is a requirements management tool that helps
# maintain structured requirements in .sdoc files.
#
# Prerequisites:
#   - StrictDoc must be installed (uv sync or pip install strictdoc)
#   - Requirements must be located in the requirements/ directory
#   - If installed with uv, commands will use 'uv run strictdoc'
# ==============================================================================

# Detect if uv is being used (uv.lock exists)
ifeq ($(shell test -f uv.lock && echo yes),yes)
    STRICTDOC := uv run strictdoc
else
    STRICTDOC := strictdoc
endif

# ------------------------------------------------------------------------------
# strictdoc-server: Launch StrictDoc Web Interface
# ------------------------------------------------------------------------------
# Starts the StrictDoc development server with a web-based interface for
# viewing, editing, and managing requirements documentation.
#
# Usage:
#   make strictdoc-server
#
# The server will:
#   - Start on http://localhost:5111 (default StrictDoc port)
#   - Provide a web UI for browsing requirements
#   - Support live editing of .sdoc files
#   - Auto-reload on file changes
#
# Press Ctrl+C to stop the server.
# ------------------------------------------------------------------------------
strictdoc-server: check-virtual-env
	$(STRICTDOC) server requirements/
.PHONY: strictdoc-server

# ------------------------------------------------------------------------------
# strictdoc-export: Generate HTML Documentation
# ------------------------------------------------------------------------------
# Exports requirements from .sdoc files to static HTML documentation.
#
# Usage:
#   make strictdoc-export
#
# This target:
#   - Reads all .sdoc files from requirements/ directory
#   - Generates a complete HTML documentation website
#   - Outputs to requirements/output/ directory
#   - Creates navigation, cross-references, and requirement traces
#
# The generated HTML can be:
#   - Opened directly in a browser (requirements/output/index.html)
#   - Hosted on a web server
#   - Committed to version control for documentation archival
# ------------------------------------------------------------------------------
strictdoc-export: check-virtual-env
	$(STRICTDOC) export requirements/ --output-dir requirements/output/
.PHONY: strictdoc-export

# ------------------------------------------------------------------------------
# strictdoc-validate: Validate Requirements Syntax and Consistency
# ------------------------------------------------------------------------------
# Checks the validity of .sdoc requirements files by performing a dry-run export.
#
# Usage:
#   make strictdoc-validate
#
# This validation performs:
#   - .sdoc file syntax validation
#   - Grammar compliance checking (RST/Jinja2 syntax)
#   - Reference integrity verification (UID uniqueness, parent-child links)
#   - Document structure validation
#   - Cross-reference consistency checks
#
# NOTE: This validates the STRUCTURE and SYNTAX of requirements, not the
# content quality or completeness. It ensures:
#   ✓ Files are parseable and well-formed
#   ✓ References point to existing requirements
#   ✓ UIDs are unique and valid
#   ✗ Does NOT validate if requirements content is correct or complete
#   ✗ Does NOT validate if requirements match the actual program behavior
#
# Exit codes:
#   0 - All validation checks passed
#   Non-zero - Validation errors found (see output for details)
# ------------------------------------------------------------------------------
strictdoc-validate: check-virtual-env
	@echo "Validating StrictDoc requirements..."
	$(STRICTDOC) export requirements/ --output-dir /tmp/strictdoc-validate-output --no-parallelization
.PHONY: strictdoc-validate

# ------------------------------------------------------------------------------
# strictdoc-help: Display Available StrictDoc Commands
# ------------------------------------------------------------------------------
# Shows available StrictDoc-related Make targets with descriptions.
#
# Usage:
#   make strictdoc-help
#
# This provides a quick reference for all StrictDoc targets defined in this
# makefile module, including their purpose and usage.
# ------------------------------------------------------------------------------
strictdoc-help:
	@echo "StrictDoc Requirements Management Targets:"
	@echo ""
	@echo "  make strictdoc-server     - Launch StrictDoc web interface"
	@echo "                              Starts server at http://localhost:5111"
	@echo "                              Provides web UI for viewing/editing requirements"
	@echo ""
	@echo "  make strictdoc-export     - Generate HTML documentation"
	@echo "                              Exports requirements to requirements/output/"
	@echo "                              Creates static HTML website from .sdoc files"
	@echo ""
	@echo "  make strictdoc-validate   - Validate requirements syntax and consistency"
	@echo "                              Checks .sdoc syntax, grammar, and references"
	@echo "                              Validates structure, not content correctness"
	@echo ""
	@echo "  make strictdoc-help       - Display this help message"
	@echo ""
	@echo "For more information about StrictDoc, visit:"
	@echo "  https://strictdoc.readthedocs.io/"
	@echo ""
.PHONY: strictdoc-help
