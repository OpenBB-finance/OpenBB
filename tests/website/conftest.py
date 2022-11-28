import pytest
from _pytest.nodes import Node
from _pytest.config.argparsing import Parser

def pytest_addoption(parser: Parser):
    parser.addoption(
        "--autodoc",
        action="store_true",
        default=False,
        help="run auto documantation tests",
    )

def pytest_runtest_setup(item: Node):
    if not item.config.getoption("--autodoc"):
        pytest.skip(msg="Runs only with option : --autodoc")
