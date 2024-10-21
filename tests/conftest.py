import pytest
import os
from click.testing import CliRunner
from mdutil.cli import cli

@pytest.fixture
def cli_runner(runner):
    """Creates an isolated file system for testing."""
    with runner.isolated_filesystem():
        yield runner

@pytest.fixture
def test_data_dir() -> str:
    """Returns the absolute path to the test data directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data")

@pytest.fixture
def sample_input_file(test_data_dir):
    """Returns path to a sample input file."""
    return os.path.join(test_data_dir, "inputs", "sample.png")

@pytest.fixture
def expected_output_file(test_data_dir):
    """Returns path to a expected output file."""
    return os.path.join(test_data_dir,"expected", "sample_processed.png")


@pytest.fixture
def results_dir() -> str:
    """Creates and returns the path to the results directory."""
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

@pytest.fixture
def cli_env():
    """Provides environment variables for CLI testing"""
    return {
            "TESTING": "true",
            "CONFIG_PATH": "/test/config"
    }
