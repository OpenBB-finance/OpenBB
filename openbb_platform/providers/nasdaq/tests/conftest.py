"""Shared fixtures for the openbb_nasdaq test suite."""

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


def patch_data(monkeypatch, payload, recorder=None):
    """Point ``get_nasdaq_data`` at a canned payload."""

    async def _data(path, **kwargs):
        if recorder is not None:
            recorder.append(path)

        return payload(path) if callable(payload) else payload

    monkeypatch.setattr("openbb_nasdaq.utils.helpers.get_nasdaq_data", _data)


def patch_asset_class(monkeypatch, asset_class):
    """Force the resolved asset class."""

    async def _resolve(symbol):
        return asset_class

    monkeypatch.setattr("openbb_nasdaq.utils.helpers.resolve_asset_class", _resolve)


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip identifying headers from recorded cassettes."""
    return {
        "filter_headers": [
            ("User-Agent", None),
            ("api_key", "MOCK_API_KEY"),
            ("x-api-token", "MOCK_API_KEY"),
        ],
        "filter_query_parameters": [
            ("api_key", "MOCK_API_KEY"),
            ("x-api-token", "MOCK_API_KEY"),
        ],
    }


@pytest.fixture(scope="session")
def factsheet_pdf() -> bytes:
    """The bundled Morningstar fact sheet for ABB Ltd, as published."""
    return (DATA_DIR / "factsheet_abb.pdf").read_bytes()


@pytest.fixture(scope="session")
def factsheet(factsheet_pdf):
    """The parsed sections of the bundled fact sheet."""
    from openbb_nasdaq.utils.factsheet import parse_factsheet

    return parse_factsheet(factsheet_pdf)


@pytest.fixture(autouse=True)
def _clear_caches():
    """Keep memoized directories and listings from leaking between tests."""
    from openbb_nasdaq.utils import helpers, nordic
    from openbb_nasdaq.utils.factsheet import fetch_factsheet

    helpers._directory_index.cache_clear()
    helpers.get_nasdaq_directory.cache_clear()
    helpers.resolve_asset_class.cache_clear()
    helpers.get_symbol_choices.cache_clear()
    helpers.get_index_symbol_choices.cache_clear()
    helpers.get_etf_symbol_choices.cache_clear()
    nordic.get_nordic_directory.cache_clear()
    nordic.get_nordic_symbol_choices.cache_clear()
    fetch_factsheet.cache_clear()
    yield
    helpers._directory_index.cache_clear()
    helpers.get_nasdaq_directory.cache_clear()
    helpers.resolve_asset_class.cache_clear()
    helpers.get_symbol_choices.cache_clear()
    helpers.get_index_symbol_choices.cache_clear()
    helpers.get_etf_symbol_choices.cache_clear()
    nordic.get_nordic_directory.cache_clear()
    nordic.get_nordic_symbol_choices.cache_clear()
    fetch_factsheet.cache_clear()


@pytest.fixture
def directory_text() -> str:
    """A minimal Nasdaq-traded symbol directory file."""
    return (
        "Nasdaq Traded|Symbol|Security Name|Listing Exchange|Market Category|ETF|"
        "Round Lot Size|Test Issue|Financial Status|CQS Symbol|NASDAQ Symbol|"
        "NextShares\n"
        "Y|AAPL|Apple Inc. - Common Stock|Q|Q|N|100|N|N|AAPL|AAPL|N\n"
        "Y|QQQ|Invesco QQQ Trust, Series 1|Q|G|Y|100|N|N|QQQ|QQQ|N\n"
        "Y|ZTEST|Nasdaq Test Issue|Q|G|N|100|Y|N|ZTEST|ZTEST|N\n"
        "File Creation Time: 0725202618:00|||||||||||\n"
    )
