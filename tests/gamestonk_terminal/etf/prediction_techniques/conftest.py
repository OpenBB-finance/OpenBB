# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from _pytest.nodes import Node

# IMPORTATION INTERNAL


def pytest_runtest_setup(item: Node):
    if not item.config.getoption("--prediction"):
        pytest.skip(msg="Runs only with option : --prediction")
