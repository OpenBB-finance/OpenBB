import pytest
from _pytest.nodes import Node


def pytest_runtest_setup(item: Node):
    if not item.config.getoption("--optimization"):
        pytest.skip(msg="Runs only with option : --optimization")
