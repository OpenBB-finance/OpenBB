"""Test the example_generator.py file."""
# pylint: disable=redefined-outer-name, protected-access


import pytest
from openbb_core.app.example_generator import ExampleGenerator


@pytest.fixture(scope="module")
def example_generator():
    """Return example generator."""
    return ExampleGenerator()


def test_docstring_generator_init(example_generator):
    """Test example generator init."""
    assert example_generator


@pytest.mark.parametrize(
    "route, model, expected",
    [
        ("", "", ""),
        ("random", "test", "obb.random()"),
        ("crypto.search", "CryptoSearch", "obb.crypto.search()"),
        (
            "crypto.price.historical",
            "CryptoHistorical",
            'obb.crypto.price.historical(symbol="BTCUSD")',
        ),
    ],
)
def test_generate(example_generator, route, model, expected):
    """Test generate example."""
    assert example_generator.generate(route, model) == expected
