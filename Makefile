PYTHON := python

TOOL := mdutil
DIST_DIR := dist
BUIL_DIR := build
TEST_DIR := tests
RESULTS_DIR := $(TEST_DIR)/results

.PHONY: setup build test clean coverage

# Setup virtual environment and install dependencies
setup:
	@$(PYTHON) -m venv .venv
	@. .venv/bin/activate && pip install pytest pytest-cov
	@mkdir -p $(RESULTS_DIR)

# Build and check dist
build:
	@$(PYTHON) -m build
	@twine check $(DIST_DIR)/*
	@pipx install . --force

# Run all tests
test:
	@$(PYTHON) -m pytest $(TEST_DIR) -v --cov=$(TOOL)

# Clean up
clean:
	@rm -rf $(DIST_DIR)
	@rm -rf $(BUIL_DIR)
	@rm -rf $(RESULTS_DIR)/*
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@find . -type d -name "__pycache__" -exec rm -r {} +

# Run tests and generate coverage report
coverage:
	@$(PYTHON) -m pytest $(TEST_DIR) -v --cov=$(TOOL) -cov-report=html
