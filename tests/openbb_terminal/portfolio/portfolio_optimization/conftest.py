import pytest
from _pytest.nodes import Node
from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--optimization",
        action="store_true",
        help="To run tests with the marker : @pytest.mark.optimization",
    )

def pytest_runtest_setup(item: Node):
    if not item.config.getoption("--optimization"):
        pytest.skip(msg="Runs only with option : --optimization")
