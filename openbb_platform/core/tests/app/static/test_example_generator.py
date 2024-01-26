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


TEST_POOL = {
    "crypto": {"symbol": "CRYPTO_SYMBOL"},
    "crypto.search": {"symbol": "CRYPTO_SEARCH_SYMBOL"},
    "crypto.price.historical": {"symbol": "CRYPTO_HISTORICAL_PRICE_SYMBOL"},
}


@pytest.mark.parametrize(
    "route, param, expected",
    [
        ("", "", "VALUE_NOT_FOUND"),
        ("random_route", "", "VALUE_NOT_FOUND"),
        ("crypto", "symbol", "CRYPTO_SYMBOL"),
        ("crypto.search", "symbol", "CRYPTO_SEARCH_SYMBOL"),
        ("crypto.price.historical", "symbol", "CRYPTO_HISTORICAL_PRICE_SYMBOL"),
        ("crypto.price.historical", "random_param", "VALUE_NOT_FOUND"),
    ],
)
def test_get_value_from_pool(example_generator, route, param, expected):
    """Test get value from pool."""
    assert example_generator._get_value_from_pool(TEST_POOL, route, param) == expected


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
