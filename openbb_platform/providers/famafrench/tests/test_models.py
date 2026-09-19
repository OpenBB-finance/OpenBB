"""Tests for the Fama-French fetcher models."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from pandas import DataFrame, MultiIndex

from openbb_famafrench.models.breakpoints import (
    FamaFrenchBreakpointFetcher,
    FamaFrenchBreakpointQueryParams,
)
from openbb_famafrench.models.country_portfolio_returns import (
    FamaFrenchCountryPortfolioReturnsFetcher,
    FamaFrenchCountryPortfolioReturnsQueryParams,
)
from openbb_famafrench.models.factors import (
    FamaFrenchFactorsFetcher,
    FamaFrenchFactorsQueryParams,
)
from openbb_famafrench.models.international_index_returns import (
    FamaFrenchInternationalIndexReturnsFetcher,
    FamaFrenchInternationalIndexReturnsQueryParams,
)
from openbb_famafrench.models.regional_portfolio_returns import (
    FamaFrenchRegionalPortfolioReturnsFetcher,
    FamaFrenchRegionalPortfolioReturnsQueryParams,
)
from openbb_famafrench.models.us_portfolio_returns import (
    FamaFrenchUSPortfolioReturnsFetcher,
    FamaFrenchUSPortfolioReturnsQueryParams,
)

# ---------------------------------------------------------------------------
# factors.py
# ---------------------------------------------------------------------------


def test_factors_query_defaults():
    """The factors query builds with default values."""
    query = FamaFrenchFactorsQueryParams()

    assert query.region == "america"
    assert query.factor == "3_factors"
    assert query.frequency == "monthly"


def test_factors_query_valid_variant():
    """The factors query accepts a valid non-default combination."""
    query = FamaFrenchFactorsQueryParams(
        region="europe", factor="5_factors", frequency="daily"
    )

    assert query.region == "europe"
    assert query.factor == "5_factors"


def test_factors_query_invalid_region():
    """An invalid region raises a validation error."""
    with pytest.raises(ValueError, match="Invalid region"):
        FamaFrenchFactorsQueryParams(region="atlantis")


def test_factors_query_invalid_factor_for_region():
    """A factor unavailable for the region raises a validation error."""
    with pytest.raises(ValueError, match="Invalid factor"):
        FamaFrenchFactorsQueryParams(region="europe", factor="st_reversal")


def test_factors_query_invalid_frequency():
    """A frequency unavailable for the factor raises a validation error."""
    with pytest.raises(ValueError, match="Invalid frequency"):
        FamaFrenchFactorsQueryParams(
            region="europe", factor="momentum", frequency="weekly"
        )


def test_factors_transform_query():
    """transform_query returns a FamaFrenchFactorsQueryParams instance."""
    query = FamaFrenchFactorsFetcher.transform_query({"region": "japan"})

    assert isinstance(query, FamaFrenchFactorsQueryParams)
    assert query.region == "japan"


def test_factors_transform_data_with_date_filters():
    """transform_data filters by start and end date."""
    frame = DataFrame(
        {
            "Mkt-RF": [1.0, 2.0, 3.0],
            "SMB": [0.1, 0.2, 0.3],
            "RF": [0.01, 0.02, 0.03],
        },
        index=["2020-01-31", "2020-02-29", "2020-03-31"],
    )
    frame.index.name = "Date"
    data = ([frame], [{"description": "Factors", "frequency": "monthly"}])
    query = FamaFrenchFactorsQueryParams(start_date="2020-02-01", end_date="2020-02-29")

    result = FamaFrenchFactorsFetcher.transform_data(query, data)

    assert len(result.result) == 1
    assert result.metadata["frequency"] == "monthly"


def test_factors_aextract_data_invalid_dataset():
    """An empty mapped dataset raises an OpenBBError."""

    class _Query:
        region = "emerging"
        factor = "3_factors"
        frequency = "monthly"

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchFactorsFetcher.aextract_data(_Query(), None))


def test_factors_aextract_data_helper_error(monkeypatch):
    """A failure inside get_portfolio_data is wrapped in an OpenBBError."""

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _boom)
    query = FamaFrenchFactorsQueryParams(region="america", factor="3_factors")

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchFactorsFetcher.aextract_data(query, None))


# ---------------------------------------------------------------------------
# breakpoints.py
# ---------------------------------------------------------------------------


def test_breakpoints_query_defaults():
    """The breakpoints query builds with default values."""
    query = FamaFrenchBreakpointQueryParams()

    assert query.breakpoint_type == "me"


def test_breakpoints_transform_query():
    """transform_query returns a FamaFrenchBreakpointQueryParams instance."""
    query = FamaFrenchBreakpointFetcher.transform_query({"breakpoint_type": "op"})

    assert isinstance(query, FamaFrenchBreakpointQueryParams)
    assert query.breakpoint_type == "op"


def test_breakpoints_transform_data_with_date_filters():
    """transform_data filters by start and end date."""
    frame = DataFrame(
        {
            "date": ["2020-01-31", "2020-02-29", "2020-03-31"],
            "num_firms": [10, 20, 30],
            **{f"percentile_{p}": [1.0, 2.0, 3.0] for p in range(5, 101, 5)},
        }
    )
    data = ([frame], ["Breakpoints metadata"])
    query = FamaFrenchBreakpointQueryParams(
        start_date="2020-02-01", end_date="2020-02-29"
    )

    result = FamaFrenchBreakpointFetcher.transform_data(query, data)

    assert len(result.result) == 1
    assert result.metadata["description"] == "Breakpoints metadata"


def test_breakpoints_transform_data_empty():
    """transform_data raises an OpenBBError when no frames are returned."""
    query = FamaFrenchBreakpointQueryParams()

    with pytest.raises(OpenBBError, match="unexpectedly empty"):
        FamaFrenchBreakpointFetcher.transform_data(query, ([], []))


def test_breakpoints_aextract_data_helper_error(monkeypatch):
    """A failure inside get_breakpoint_data is wrapped in an OpenBBError."""

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_breakpoint_data", _boom)
    query = FamaFrenchBreakpointQueryParams()

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchBreakpointFetcher.aextract_data(query, None))


# ---------------------------------------------------------------------------
# us_portfolio_returns.py / regional_portfolio_returns.py
# ---------------------------------------------------------------------------


def _portfolio_frame():
    """A returns frame with a string column that is entirely missing data."""
    frame = DataFrame(
        {
            "Lo 30": ["1.0", "2.0", "3.0"],
            "Hi 30": ["-99.99", "-99.99", "-99.99"],
        },
        index=["2020-01-31", "2020-02-29", "2020-03-31"],
    )
    frame.index.name = "Date"
    return frame


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
        (
            FamaFrenchRegionalPortfolioReturnsFetcher,
            FamaFrenchRegionalPortfolioReturnsQueryParams,
        ),
    ],
)
def test_portfolio_transform_query(fetcher, query_cls):
    """transform_query returns the expected QueryParams type."""
    query = fetcher.transform_query({})

    assert isinstance(query, query_cls)


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
        (
            FamaFrenchRegionalPortfolioReturnsFetcher,
            FamaFrenchRegionalPortfolioReturnsQueryParams,
        ),
    ],
)
def test_portfolio_transform_data(fetcher, query_cls):
    """transform_data drops empty columns, casts, and filters by date."""
    query = query_cls(measure="value", start_date="2020-02-01", end_date="2020-02-29")
    data = ([_portfolio_frame()], [{"description": "Portfolio"}])

    result = fetcher.transform_data(query, data)

    assert result.result
    # The fully-missing column was dropped.
    assert all(r.portfolio == "Lo 30" for r in result.result)
    assert all(r.measure == "value" for r in result.result)


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
        (
            FamaFrenchRegionalPortfolioReturnsFetcher,
            FamaFrenchRegionalPortfolioReturnsQueryParams,
        ),
    ],
)
def test_portfolio_transform_data_number_of_firms(fetcher, query_cls):
    """The number_of_firms measure casts values to integers."""
    frame = DataFrame(
        {"Lo 30": ["10", "20"]},
        index=["2020-01-31", "2020-02-29"],
    )
    frame.index.name = "Date"
    query = query_cls(measure="number_of_firms")
    data = ([frame], [{"description": "Portfolio"}])

    result = fetcher.transform_data(query, data)

    assert all(isinstance(r.value, int) for r in result.result)


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
        (
            FamaFrenchRegionalPortfolioReturnsFetcher,
            FamaFrenchRegionalPortfolioReturnsQueryParams,
        ),
    ],
)
def test_portfolio_transform_data_empty(fetcher, query_cls):
    """transform_data raises an OpenBBError when no frames are returned."""
    with pytest.raises(OpenBBError, match="returned empty"):
        fetcher.transform_data(query_cls(), ([], []))


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
        (
            FamaFrenchRegionalPortfolioReturnsFetcher,
            FamaFrenchRegionalPortfolioReturnsQueryParams,
        ),
    ],
)
def test_portfolio_aextract_data_helper_error(monkeypatch, fetcher, query_cls):
    """A failure inside get_portfolio_data is wrapped in an OpenBBError."""

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _boom)

    with pytest.raises(OpenBBError):
        asyncio.run(fetcher.aextract_data(query_cls(), None))


def test_us_portfolio_aextract_data_daily(monkeypatch):
    """A daily portfolio passes a None frequency to get_portfolio_data."""
    captured = {}

    def _capture(dataset, measure=None, frequency=None):
        captured["frequency"] = frequency
        return ([], [])

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _capture)
    query = FamaFrenchUSPortfolioReturnsQueryParams(
        portfolio="portfolios_formed_on_me_daily"
    )

    asyncio.run(FamaFrenchUSPortfolioReturnsFetcher.aextract_data(query, None))

    assert captured["frequency"] is None


def test_regional_portfolio_aextract_data_daily(monkeypatch):
    """A daily regional portfolio passes a None frequency to get_portfolio_data."""
    captured = {}

    def _capture(dataset, measure=None, frequency=None):
        captured["frequency"] = frequency
        return ([], [])

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _capture)
    query = FamaFrenchRegionalPortfolioReturnsQueryParams(
        portfolio="europe_6_portfolios_me_be-me_daily"
    )

    asyncio.run(FamaFrenchRegionalPortfolioReturnsFetcher.aextract_data(query, None))

    assert captured["frequency"] is None


# ---------------------------------------------------------------------------
# country_portfolio_returns.py / international_index_returns.py
# ---------------------------------------------------------------------------


def _international_frame(multiindex: bool = False):
    """A returns frame with a fully-missing column and an optional MultiIndex."""
    frame = DataFrame(
        {
            "Mkt": ["1.0", "2.0", "3.0"],
            "High": ["0.5", "0.6", "0.7"],
            "Low": ["-99.99", "-99.99", "-99.99"],
        },
        index=["2020-01-31", "2020-02-29", "2020-03-31"],
    )
    frame.index.name = "Date"
    if multiindex:
        frame.columns = MultiIndex.from_arrays(
            [["", "BE/ME", "BE/ME"], ["Mkt", "High", "Low"]]
        )
    return frame


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_transform_query(fetcher, query_cls):
    """transform_query returns the expected QueryParams type."""
    query = fetcher.transform_query({})

    assert isinstance(query, query_cls)


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_transform_data(fetcher, query_cls):
    """transform_data drops empty columns and filters by date."""
    query = query_cls(measure="usd", start_date="2020-02-01", end_date="2020-02-29")
    data = ([_international_frame()], [{"description": "Index"}])

    result = fetcher.transform_data(query, data)

    assert result.result
    assert "description" in result.metadata


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_transform_data_multiindex(fetcher, query_cls):
    """transform_data flattens MultiIndex columns."""
    query = query_cls(measure="usd")
    data = ([_international_frame(multiindex=True)], [{"description": "Index"}])

    result = fetcher.transform_data(query, data)

    assert result.result


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_transform_data_ratios_firms(fetcher, query_cls):
    """The ratios measure casts the firms column to integers."""
    frame = DataFrame(
        {
            "firms": ["100", "200"],
            "B/M": ["1.0", "2.0"],
        },
        index=["2020-12-31", "2021-12-31"],
    )
    frame.index.name = "Date"
    query = query_cls(measure="ratios")
    data = ([frame], [{"description": "Ratios"}])

    result = fetcher.transform_data(query, data)

    assert all(isinstance(r.firms, int) for r in result.result)


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_transform_data_empty(fetcher, query_cls):
    """transform_data raises an OpenBBError when no frames are returned."""
    with pytest.raises(OpenBBError, match="returned empty"):
        fetcher.transform_data(query_cls(), ([], []))


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_aextract_data_helper_error(monkeypatch, fetcher, query_cls):
    """A failure inside get_international_portfolio is wrapped in an OpenBBError."""

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(
        "openbb_famafrench.utils.helpers.get_international_portfolio", _boom
    )

    with pytest.raises(OpenBBError):
        asyncio.run(fetcher.aextract_data(query_cls(), None))


@pytest.mark.parametrize(
    ("fetcher", "query_cls"),
    [
        (
            FamaFrenchCountryPortfolioReturnsFetcher,
            FamaFrenchCountryPortfolioReturnsQueryParams,
        ),
        (
            FamaFrenchInternationalIndexReturnsFetcher,
            FamaFrenchInternationalIndexReturnsQueryParams,
        ),
    ],
)
def test_international_aextract_data_ratios_monthly_warns(
    monkeypatch, fetcher, query_cls
):
    """The ratios measure with monthly frequency warns and forces annual."""
    captured = {}

    def _capture(*args, **kwargs):
        captured["frequency"] = kwargs.get("frequency")
        return ([], [])

    monkeypatch.setattr(
        "openbb_famafrench.utils.helpers.get_international_portfolio", _capture
    )
    query = query_cls(measure="ratios", frequency="monthly")

    with pytest.warns(UserWarning, match="annual"):
        asyncio.run(fetcher.aextract_data(query, None))

    assert captured["frequency"] == "annual"
