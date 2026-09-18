"""Tests for the generated CME catalog, specifications, and options chains."""

from datetime import date
from unittest.mock import AsyncMock, patch

from openbb_core.provider.utils.helpers import run_async

from openbb_cme.models.contract_specs import CMEContractSpecsFetcher
from openbb_cme.models.options_chains import CMEOptionsChainsFetcher
from openbb_cme.models.products import CMEProductsFetcher
from openbb_cme.utils.catalog import (
    clear_catalog_cache,
    fetch_contract_specifications,
    fetch_product_catalog,
)

_ES_PRODUCT = {
    "product_id": 133,
    "guid": "ES-GUID",
    "symbol": "ES",
    "name": "E-mini S&P 500 Futures",
    "product_type": "Futures",
    "asset_class": "Equities",
    "subgroup": "S&P",
    "category": None,
    "subcategory": None,
    "exchange": "CME",
    "venues": ["Globex", "ClearPort"],
    "globex_traded": True,
    "floor_traded": False,
    "volume": 1_000_000,
    "open_interest": 2_000_000,
    "codes": {"product": "ES", "globex": "ES", "clearing": "ES"},
    "specification_url": "https://www.cmegroup.com/markets/es",
}

_ES_OPTION_PRODUCT = {
    **_ES_PRODUCT,
    "product_id": 138,
    "guid": "ES-OPTION-GUID",
    "name": "E-mini S&P 500 Options",
    "product_type": "Options",
}

_SPECS = {
    "ProductID": 138,
    "ProductName": "E-mini S&P 500 Options",
    "ContractUnit": "$50 x S&P 500 Index",
    "PriceQuotation": "U.S. dollars per index point",
    "MinimumPriceFluctuation": {
        "ticks": [{"type": "Outright", "mintk": "0.25 points<br />$12.50"}]
    },
    "ProductCode": {"CmeGlobex": "ES"},
    "ListedContracts": {
        "contractMonthsList": [{"type": "Default", "contrMonth": "Quarterly"}]
    },
    "TradingHours": {"vandhr": [{"venue": "Globex", "hours": "Sunday-Friday"}]},
    "SettlementMethod": "Financially Settled",
    "ExerciseStyle": "American",
    "Underlying": "E-mini S&P 500 Futures",
}


def _raw_product(product_id: int, symbol: str, name: str, group: str) -> dict:
    return {
        "id": product_id,
        "guid": f"{symbol}-GUID",
        "prodCode": symbol,
        "prodGroup": symbol,
        "name": name,
        "clearing": symbol,
        "globex": symbol,
        "floor": "-",
        "floorTraded": False,
        "globexTraded": True,
        "cpc": symbol,
        "venues": "Globex ClearPort",
        "cleared": "Futures",
        "exch": "CME",
        "url": f"/markets/{symbol.lower()}",
        "cat": "-",
        "subCat": "-",
        "group": group,
        "subGroup": "Benchmark",
        "vol": "1,234",
        "oi": "5,678",
    }


def test_catalog_fetches_every_page_and_normalizes_metadata():
    """The catalog follows CME pagination and normalizes published fields."""
    responses = [
        {
            "products": [_raw_product(133, "ES", "E-mini S&P 500 Futures", "Equities")],
            "props": {"pageTotal": 2},
        },
        {
            "products": [_raw_product(437, "GC", "Gold Futures", "Metals")],
            "props": {"pageTotal": 2},
        },
    ]
    clear_catalog_cache()
    with patch(
        "openbb_cme.utils.helpers._get_json",
        new=AsyncMock(side_effect=responses),
    ) as mock_get:
        result = run_async(fetch_product_catalog, "Futures", use_cache=False)

    assert len(result) == 2
    assert {row["symbol"] for row in result} == {"ES", "GC"}
    assert {row["asset_class"] for row in result} == {"Equities", "Metals"}
    assert result[0]["volume"] == 1234
    assert mock_get.await_count == 2
    clear_catalog_cache()


def test_products_fetcher_filters_generated_catalog():
    """Catalog filters expose products across asset classes."""
    with patch(
        "openbb_cme.models.products.search_products",
        new=AsyncMock(return_value=[_ES_PRODUCT]),
    ) as mock_search:
        result = run_async(
            CMEProductsFetcher.fetch_data,
            {"asset_class": "Equities", "product_type": "Futures"},
            {},
        )

    assert result[0].product_id == 133
    assert result[0].codes["globex"] == "ES"
    mock_search.assert_awaited_once()


def test_contract_specs_strip_exchange_html():
    """Specification normalization preserves structure while removing HTML."""
    with patch(
        "openbb_cme.utils.helpers._get_json",
        new=AsyncMock(return_value=_SPECS),
    ):
        result = run_async(fetch_contract_specifications, 138)

    tick = result["MinimumPriceFluctuation"]["ticks"][0]["mintk"]
    assert tick == "0.25 points\n$12.50"


def test_contract_specs_fetcher_returns_complete_payload():
    """The contract-spec endpoint joins catalog identity with full CME metadata."""
    with (
        patch(
            "openbb_cme.models.contract_specs.search_products",
            new=AsyncMock(return_value=[_ES_OPTION_PRODUCT]),
        ),
        patch(
            "openbb_cme.models.contract_specs.fetch_contract_specifications",
            new=AsyncMock(return_value=_SPECS),
        ),
    ):
        result = run_async(
            CMEContractSpecsFetcher.fetch_data,
            {"product_id": 138},
            {},
        )

    assert result[0].product_type == "Options"
    assert result[0].exercise_style == "American"
    assert result[0].specifications["Underlying"] == "E-mini S&P 500 Futures"


def test_options_chains_normalizes_calls_and_puts():
    """Option settlements become a standard OpenBB options chain."""
    expirations = [
        {
            "product_id": 138,
            "option_type": "AME",
            "name": "E-mini S&P 500 Options",
            "label": "Sep 2026",
            "month_year": "U26",
            "contract_id": "ESU26",
            "expiration_date": date(2026, 9, 18),
            "trade_dates": ["07/22/2026"],
        }
    ]
    settlements = [
        {
            "strike": "7500.00",
            "type": "Call",
            "open": "100.25",
            "high": "110.00",
            "low": "95.00",
            "last": "105.50A",
            "change": "+5.25",
            "settle": "106.00",
            "volume": "1,200",
            "openInterest": "8,500",
        },
        {
            "strike": "7500.00",
            "type": "Put",
            "open": "80.00",
            "high": "85.00",
            "low": "72.00",
            "last": "75.25",
            "change": "-4.75",
            "settle": "75.00",
            "volume": "900",
            "openInterest": "7,000",
        },
    ]
    with (
        patch(
            "openbb_cme.models.options_chains.resolve_product",
            new=AsyncMock(return_value=_ES_OPTION_PRODUCT),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_option_expirations",
            new=AsyncMock(return_value=expirations),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_contract_specifications",
            new=AsyncMock(return_value=_SPECS),
        ),
        patch(
            "openbb_cme.models.options_chains.fetch_option_settlements",
            new=AsyncMock(return_value=settlements),
        ),
    ):
        result = run_async(
            CMEOptionsChainsFetcher.fetch_data,
            {
                "symbol": "ES",
                "expiration": "2026-09-18",
                "date": "2026-07-22",
            },
            {},
        )

    assert result.option_type == ["call", "put"]
    assert result.contract_symbol == ["ESU26-7500-C", "ESU26-7500-P"]
    assert result.settlement_price == [106.0, 75.0]
    assert result.open_interest == [8500.0, 7000.0]
    assert result.contract_size == [50.0, 50.0]
