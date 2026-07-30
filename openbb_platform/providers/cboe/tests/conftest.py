"""Shared fixtures for the openbb_cboe test suite."""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration: strip the User-Agent header from recorded cassettes."""
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [None],
    }


@pytest.fixture
def raw_options_chain():
    """Raw Cboe options-chain payload for CLX, as returned by the endpoint.

    A fresh parse per test: ``transform_data`` pops the options list off the
    payload, so a shared instance would be drained by the first consumer.
    """
    return json.loads((DATA_DIR / "options_clx.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def options_chain():
    """Parsed ``CboeOptionsChainsData`` built from the bundled CLX payload."""
    from openbb_cboe.models.options_chains import (
        CboeOptionsChainsFetcher,
        CboeOptionsChainsQueryParams,
    )

    payload = json.loads((DATA_DIR / "options_clx.json").read_text(encoding="utf-8"))
    query = CboeOptionsChainsQueryParams(symbol="CLX")

    return CboeOptionsChainsFetcher.transform_data(query, payload).result


@pytest.fixture(autouse=True)
def _clear_symbol_cache():
    """Keep the options data handler's per-symbol cache out of other tests."""
    from openbb_cboe.utils.options import data_handler

    data_handler.LOADED_SYMBOLS.clear()
    yield
    data_handler.LOADED_SYMBOLS.clear()


@pytest.fixture
def index_directory():
    """Minimal Cboe index directory frame."""
    from pandas import DataFrame

    return DataFrame(
        [
            {
                "index_symbol": "BUK100P",
                "name": "Cboe UK 100",
                "description": "UK large cap",
                "source": "eu_proprietary_index",
                "currency": "GBP",
            },
            {
                "index_symbol": "AAVE10RP",
                "name": "Cboe Apple 10 Index",
                "description": "US index",
                "source": "us_index",
                "currency": "USD",
            },
            {
                "index_symbol": "X2C",
                "name": "CXA 200 Price Return Index",
                "description": "Cboe Australia 200",
                "source": "au_proprietary_index",
                "currency": "AUD",
            },
        ]
    )


@pytest.fixture
def company_directory():
    """Minimal Cboe company directory frame, indexed by symbol."""
    from pandas import DataFrame

    return DataFrame(
        [
            {
                "symbol": "AAPL",
                "name": "APPLE INC",
                "dpm_name": "DPM",
                "post_station": "1",
            },
            {
                "symbol": "SPY",
                "name": "SPDR S&P 500 ETF",
                "dpm_name": "DPM",
                "post_station": "2",
            },
        ]
    ).set_index("symbol")
