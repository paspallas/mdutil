
TOOL := mdutil
TEST_DIR := tests
RESULTS_DIR := $(TEST_DIR)/results


all: test

# Setup virtual environment and install dependencies
setup:
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install pytest pytest-cov
	mkdir -p $(RESULTS_DIR)

# Run all tests
test:
	$(PYTHON) -m pytest $(TEST_DIR) -v --cov=$(TOOL)

# Clean up
clean:
	rm -rf $(RESULTS_DIR)/*
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -r {} +

# Run tests and generate coverage report
coverage:
	$(PYTHON) -m pytest $(TEST_DIR) -v --cov=$(TOOL) -cov-report=html
