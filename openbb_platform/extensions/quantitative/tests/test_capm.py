"""Tests for CAPM data preparation."""

from datetime import date
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import pytest
from openbb_core.provider.abstract.data import Data
from openbb_quantitative.helpers import (
    FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN,
    FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN,
    FAMA_FRENCH_MONTHLY_FACTORS_FILE,
    FAMA_FRENCH_RISK_FREE_RETURN_COLUMN,
    FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN,
    fit_capm,
    get_fama_raw,
    prepare_monthly_capm_data,
)
from openbb_quantitative.quantitative_router import capm


def test_get_fama_raw_reads_local_zip(tmp_path):
    """The Fama-French parser should support deterministic local ZIP fixtures."""
    archive_path = tmp_path / "fama_french_factors.zip"
    csv_data = "\n".join(
        [
            "Fixture generated for unit testing",
            "Monthly factors in percent",
            "",
            ",Mkt-RF,SMB,HML,RF",
            "202301,1.00,-2.00,3.00,0.10",
            "202302,2.00,-1.00,4.00,0.20",
            "202303,3.00,0.00,5.00,0.30",
            "",
            " Annual Factors: January-December ",
            ",Mkt-RF,SMB,HML,RF",
            "2023,6.00,-3.00,12.00,0.60",
        ]
    )
    with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(FAMA_FRENCH_MONTHLY_FACTORS_FILE, csv_data)

    result = get_fama_raw(
        date(2023, 2, 1),
        date(2023, 3, 31),
        url=archive_path.as_uri(),
    )

    assert list(result.index) == [
        pd.Timestamp("2023-02-01"),
        pd.Timestamp("2023-03-01"),
    ]
    assert list(result.columns) == [
        FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN,
        FAMA_FRENCH_SMALL_MINUS_BIG_RETURN_COLUMN,
        FAMA_FRENCH_HIGH_MINUS_LOW_RETURN_COLUMN,
        FAMA_FRENCH_RISK_FREE_RETURN_COLUMN,
    ]
    assert result.iloc[0].to_list() == pytest.approx([0.02, -0.01, 0.04, 0.002])


def test_prepare_monthly_capm_data_aligns_months_and_uses_market_excess_return():
    """Daily prices should become monthly returns aligned by calendar month."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2023-01-31",
                    "2023-02-28",
                    "2023-03-31",
                    "2023-04-28",
                ]
            ),
            "close": [100.0, 102.0, 105.06, 109.2624],
        }
    )
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: [0.01, 0.02, 0.03, 0.04],
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: [0.001, 0.002, 0.003, 0.004],
        },
        index=pd.to_datetime(["2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01"]),
    )

    result = prepare_monthly_capm_data(data, factors, "close")

    assert list(result.index.astype(str)) == ["2023-02", "2023-03", "2023-04"]
    assert result["excess_return"].to_list() == pytest.approx([0.018, 0.027, 0.036])
    assert result["excess_mkt"].to_list() == pytest.approx([0.02, 0.03, 0.04])


def test_prepare_monthly_capm_data_uses_month_end_prices():
    """The result must use month-end prices, not isolated month-start returns."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2023-01-30",
                    "2023-01-31",
                    "2023-02-01",
                    "2023-02-28",
                    "2023-03-01",
                    "2023-03-31",
                    "2023-04-03",
                    "2023-04-28",
                ]
            ),
            "close": [99.0, 100.0, 101.0, 110.0, 111.0, 121.0, 122.0, 133.1],
        }
    )
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: [0.01, 0.02, 0.03],
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: [0.0, 0.0, 0.0],
        },
        index=pd.to_datetime(["2023-02-01", "2023-03-01", "2023-04-01"]),
    )

    result = prepare_monthly_capm_data(data, factors, "close")

    assert result["excess_return"].to_list() == pytest.approx([0.10, 0.10, 0.10])


def test_prepare_monthly_capm_data_requires_three_aligned_observations():
    """An underdetermined or two-point regression should fail clearly."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2023-01-31", "2023-02-28", "2023-03-31"]),
            "close": [100.0, 101.0, 102.0],
        }
    )
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: [0.01, 0.02],
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: [0.001, 0.001],
        },
        index=pd.to_datetime(["2023-02-01", "2023-03-01"]),
    )

    with pytest.raises(ValueError, match="at least 3 aligned monthly"):
        prepare_monthly_capm_data(data, factors, "close")


def test_prepare_monthly_capm_data_rejects_constant_market_returns():
    """CAPM beta is unidentified when market excess returns do not vary."""
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2023-01-31", "2023-02-28", "2023-03-31", "2023-04-28"]
            ),
            "close": [100.0, 101.0, 102.0, 103.0],
        }
    )
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: [0.02, 0.02, 0.02],
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: [0.001, 0.001, 0.001],
        },
        index=pd.to_datetime(["2023-02-01", "2023-03-01", "2023-04-01"]),
    )

    with pytest.raises(ValueError, match="variation in market excess returns"):
        prepare_monthly_capm_data(data, factors, "close")


def test_fit_capm_recovers_known_beta():
    """The prices-to-regression pipeline should recover an exact CAPM beta."""
    market_excess = [-0.03, -0.01, 0.01, 0.02, 0.04]
    risk_free = [0.001, 0.002, 0.001, 0.003, 0.002]
    monthly_returns = [
        rf + 0.002 + 1.5 * market for market, rf in zip(market_excess, risk_free)
    ]
    prices = [100.0]
    for monthly_return in monthly_returns:
        prices.append(prices[-1] * (1 + monthly_return))

    data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2023-01-31",
                    "2023-02-28",
                    "2023-03-31",
                    "2023-04-28",
                    "2023-05-31",
                    "2023-06-30",
                ]
            ),
            "close": prices,
        }
    )
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: market_excess,
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: risk_free,
        },
        index=pd.to_datetime(
            [
                "2023-02-01",
                "2023-03-01",
                "2023-04-01",
                "2023-05-01",
                "2023-06-01",
            ]
        ),
    )

    beta, r_squared = fit_capm(prepare_monthly_capm_data(data, factors, "close"))

    assert beta == pytest.approx(1.5)
    assert r_squared == pytest.approx(1.0)


def test_capm_router_uses_monthly_factors(monkeypatch):
    """The CAPM command should run the complete local regression pipeline."""
    market_excess = [-0.03, -0.01, 0.01, 0.02, 0.04]
    risk_free = [0.001, 0.002, 0.001, 0.003, 0.002]
    monthly_returns = [
        rf + 0.002 + 1.5 * market for market, rf in zip(market_excess, risk_free)
    ]
    prices = [100.0]
    for monthly_return in monthly_returns:
        prices.append(prices[-1] * (1 + monthly_return))

    dates = pd.to_datetime(
        [
            "2023-01-31",
            "2023-02-28",
            "2023-03-31",
            "2023-04-28",
            "2023-05-31",
            "2023-06-30",
        ]
    )
    data = [
        Data(date=timestamp.date(), close=price)
        for timestamp, price in zip(dates, prices)
    ]
    factors = pd.DataFrame(
        {
            FAMA_FRENCH_MARKET_EXCESS_RETURN_COLUMN: market_excess,
            FAMA_FRENCH_RISK_FREE_RETURN_COLUMN: risk_free,
        },
        index=pd.to_datetime(
            [
                "2023-02-01",
                "2023-03-01",
                "2023-04-01",
                "2023-05-01",
                "2023-06-01",
            ]
        ),
    )

    def get_factors(start_date, end_date):
        assert start_date == date(2023, 1, 31)
        assert end_date == date(2023, 6, 30)
        return factors

    monkeypatch.setattr("openbb_quantitative.helpers.get_fama_raw", get_factors)

    result = capm(data, "close")

    assert result.results.market_risk == pytest.approx(1.5)
    assert result.results.systematic_risk == pytest.approx(1.0)
    assert result.results.idiosyncratic_risk == pytest.approx(0.0)
