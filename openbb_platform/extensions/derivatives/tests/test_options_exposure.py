"""Tests for options exposure helpers and command."""

from asyncio import run
from datetime import date

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.obbject import OBBject
from openbb_core.provider.standard_models.options_chains import OptionsChainsData
from openbb_derivatives.options.options_router import exposure

SYNTHETIC_OPTIONS_CHAIN = [
    {
        "expiration": "2030-01-17",
        "strike": 100,
        "option_type": "call",
        "open_interest": 10,
        "volume": 5,
        "delta": 0.6,
        "gamma": 0.02,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 100,
        "option_type": "put",
        "open_interest": 8,
        "volume": 4,
        "delta": -0.4,
        "gamma": 0.03,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 105,
        "option_type": "call",
        "open_interest": 20,
        "volume": 10,
        "delta": 0.4,
        "gamma": 0.01,
        "underlying_price": 100,
        "contract_size": 100,
    },
    {
        "expiration": "2030-01-17",
        "strike": 95,
        "option_type": "put",
        "open_interest": 12,
        "volume": 7,
        "delta": -0.25,
        "gamma": 0.015,
        "underlying_price": 100,
        "contract_size": 100,
    },
]


def test_options_exposure_aggregates_by_strike() -> None:
    """Test options exposure aggregation by strike."""
    result = run(exposure(data=SYNTHETIC_OPTIONS_CHAIN, by="strike"))

    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) == 3

    strike_100 = next(row for row in result.results if row["strike"] == 100)
    assert strike_100["call_open_interest"] == 10
    assert strike_100["put_open_interest"] == 8
    assert strike_100["total_open_interest"] == 18
    assert strike_100["total_gex"] == 4400
    assert strike_100["net_gex"] == -400
    assert strike_100["total_dex"] == 92000
    assert strike_100["net_dex"] == 28000

    summary = result.extra["summary"]
    assert summary["total_open_interest"] == 50
    assert summary["total_gex"] == 8200
    assert summary["net_gex"] == -200
    assert summary["put_call_ratio_open_interest"] == 0.6667
    assert summary["gamma_wall"] == 105
    assert summary["put_gamma_wall"] == 100


def test_options_exposure_serializes_expiration_groups() -> None:
    """Test expiration grouping serializes date keys to API-safe strings."""
    result = run(exposure(data=SYNTHETIC_OPTIONS_CHAIN, by="expiration"))

    assert len(result.results) == 1
    assert result.results[0]["expiration"] == "2030-01-17"
    assert result.results[0]["total_open_interest"] == 50
    assert result.extra["summary"]["by"] == "expiration"


def test_options_exposure_uses_supplied_underlying_price() -> None:
    """Test greeks exposure can use a command-level underlying price."""
    records = [
        {key: value for key, value in record.items() if key != "underlying_price"}
        for record in SYNTHETIC_OPTIONS_CHAIN
    ]

    result = run(exposure(data=records, underlying_price=100, by="strike"))

    strike_100 = next(row for row in result.results if row["strike"] == 100)
    assert strike_100["net_gex"] == -400
    assert result.extra["summary"]["gamma_wall"] == 105


def test_options_exposure_filters_otm_options() -> None:
    """Test OTM filtering uses the available underlying price."""
    result = run(exposure(data=SYNTHETIC_OPTIONS_CHAIN, option_type="otm"))

    assert {row["strike"] for row in result.results} == {95, 105}
    assert result.extra["summary"]["total_open_interest"] == 32


def test_options_exposure_omits_greeks_when_not_available() -> None:
    """Test exposure output does not report zero greeks when greeks are unavailable."""
    records = [
        {
            key: value
            for key, value in record.items()
            if key not in {"delta", "gamma", "underlying_price"}
        }
        for record in SYNTHETIC_OPTIONS_CHAIN
    ]

    result = run(exposure(data=records, by="strike"))
    strike_100 = next(row for row in result.results if row["strike"] == 100)

    assert "total_dex" not in strike_100
    assert "total_gex" not in strike_100
    assert "net_dex" not in result.extra["summary"]
    assert "net_gex" not in result.extra["summary"]


def test_options_exposure_omits_greeks_when_underlying_price_is_null() -> None:
    """Test null underlying prices do not become zero exposure metrics."""
    records = [
        {**record, "underlying_price": None} for record in SYNTHETIC_OPTIONS_CHAIN
    ]

    result = run(exposure(data=records, by="strike"))
    strike_100 = next(row for row in result.results if row["strike"] == 100)

    assert "total_dex" not in strike_100
    assert "total_gex" not in strike_100
    assert "gamma_wall" not in result.extra["summary"]


def test_options_exposure_uses_options_chains_last_price() -> None:
    """Test OptionsChainsData.last_price is honored by the exposure command."""
    data = OptionsChainsData(
        contract_symbol=[
            "FAKE300117C00100000",
            "FAKE300117P00100000",
        ],
        expiration=[date(2030, 1, 17), date(2030, 1, 17)],
        strike=[100, 100],
        option_type=["call", "put"],
        open_interest=[10, 8],
        volume=[5, 4],
        delta=[0.6, -0.4],
        gamma=[0.02, 0.03],
        contract_size=[100, 100],
    )
    data.last_price = 100

    result = run(exposure(data=data, by="strike"))

    assert result.results[0]["net_gex"] == -400
    assert result.extra["summary"]["put_gamma_wall"] == 100


def test_options_exposure_uses_eod_date_for_derived_dte() -> None:
    """Test missing DTE is derived from eod_date when historical rows provide it."""
    records = [
        {
            **record,
            "dte": None,
            "eod_date": "2030-01-10",
        }
        for record in SYNTHETIC_OPTIONS_CHAIN
    ]

    result = run(exposure(data=records, dte_min=7, dte_max=7, by="strike"))

    assert len(result.results) == 3
    assert result.extra["summary"]["total_open_interest"] == 50


def test_options_exposure_requires_underlying_price_for_moneyness_filters() -> None:
    """Test moneyness filters fail early without an underlying price."""
    records = [
        {key: value for key, value in record.items() if key != "underlying_price"}
        for record in SYNTHETIC_OPTIONS_CHAIN
    ]

    with pytest.raises(OpenBBError, match="Last price must be provided"):
        run(exposure(data=records, option_type="otm"))
