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


def test_factors_query_defaults():
    query = FamaFrenchFactorsQueryParams()

    assert query.region == "america"
    assert query.factor == "3_factors"
    assert query.frequency == "monthly"


def test_factors_query_valid_variant():
    query = FamaFrenchFactorsQueryParams(
        region="europe", factor="5_factors", frequency="daily"
    )

    assert query.region == "europe"
    assert query.factor == "5_factors"


def test_factors_query_invalid_region():
    with pytest.raises(ValueError, match="Invalid region"):
        FamaFrenchFactorsQueryParams(region="atlantis")


def test_factors_query_invalid_factor_for_region():
    with pytest.raises(ValueError, match="Invalid factor"):
        FamaFrenchFactorsQueryParams(region="europe", factor="st_reversal")


def test_factors_query_invalid_frequency():
    with pytest.raises(ValueError, match="Invalid frequency"):
        FamaFrenchFactorsQueryParams(
            region="europe", factor="momentum", frequency="weekly"
        )


def test_factors_transform_query():
    query = FamaFrenchFactorsFetcher.transform_query({"region": "japan"})

    assert isinstance(query, FamaFrenchFactorsQueryParams)
    assert query.region == "japan"


def test_factors_transform_data_with_date_filters():
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

    class _Query:
        region = "emerging"
        factor = "3_factors"
        frequency = "monthly"

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchFactorsFetcher.aextract_data(_Query(), None))


def test_factors_aextract_data_helper_error(monkeypatch):

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _boom)
    query = FamaFrenchFactorsQueryParams(region="america", factor="3_factors")

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchFactorsFetcher.aextract_data(query, None))


def test_breakpoints_query_defaults():
    query = FamaFrenchBreakpointQueryParams()

    assert query.breakpoint_type == "me"


def test_breakpoints_transform_query():
    query = FamaFrenchBreakpointFetcher.transform_query({"breakpoint_type": "op"})

    assert isinstance(query, FamaFrenchBreakpointQueryParams)
    assert query.breakpoint_type == "op"


def test_breakpoints_transform_data_with_date_filters():
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
    query = FamaFrenchBreakpointQueryParams()

    with pytest.raises(OpenBBError, match="unexpectedly empty"):
        FamaFrenchBreakpointFetcher.transform_data(query, ([], []))


def test_breakpoints_aextract_data_helper_error(monkeypatch):

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_breakpoint_data", _boom)
    query = FamaFrenchBreakpointQueryParams()

    with pytest.raises(OpenBBError):
        asyncio.run(FamaFrenchBreakpointFetcher.aextract_data(query, None))


def _portfolio_frame():
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
    query = query_cls(measure="value", start_date="2020-02-01", end_date="2020-02-29")
    data = ([_portfolio_frame()], [{"description": "Portfolio"}])

    result = fetcher.transform_data(query, data)

    assert result.result
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

    def _boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("openbb_famafrench.utils.helpers.get_portfolio_data", _boom)

    with pytest.raises(OpenBBError):
        asyncio.run(fetcher.aextract_data(query_cls(), None))


def test_us_portfolio_aextract_data_daily(monkeypatch):
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


def _international_frame(multiindex: bool = False):
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


DATES = ["2020-01-31", "2020-02-29", "2020-03-31"]
PORTFOLIO_FETCHERS = [
    (FamaFrenchUSPortfolioReturnsFetcher, FamaFrenchUSPortfolioReturnsQueryParams),
    (
        FamaFrenchRegionalPortfolioReturnsFetcher,
        FamaFrenchRegionalPortfolioReturnsQueryParams,
    ),
]
INTERNATIONAL_FETCHERS = [
    (
        FamaFrenchCountryPortfolioReturnsFetcher,
        FamaFrenchCountryPortfolioReturnsQueryParams,
    ),
    (
        FamaFrenchInternationalIndexReturnsFetcher,
        FamaFrenchInternationalIndexReturnsQueryParams,
    ),
]


def test_factors_transform_data_missing_values():
    frame = DataFrame(
        {"Mkt-RF": ["1.0", "-99.99"], "SMB": ["0.1", "0.2"], "RF": ["0.01", "-999"]},
        index=DATES[:2],
    )
    frame.index.name = "Date"

    result = FamaFrenchFactorsFetcher.transform_data(
        FamaFrenchFactorsQueryParams(), ([frame], [{"description": "Factors"}])
    ).result

    assert [r.mkt_rf for r in result] == [1.0, None]
    assert [r.smb for r in result] == [0.1, 0.2]
    assert [r.rf for r in result] == [0.01, None]


@pytest.mark.parametrize(("fetcher", "query_cls"), PORTFOLIO_FETCHERS)
def test_portfolio_transform_data_missing_values(fetcher, query_cls):
    frame = DataFrame(
        {
            "Lo 30": ["1.0", "-99.99", "3.0"],
            "Hi 30": ["-999", "2.0", "-99.990"],
            "Med 40": ["-99.99", "-999", "-999.00"],
        },
        index=DATES,
    )
    frame.index.name = "Date"

    result = fetcher.transform_data(
        query_cls(measure="value"), ([frame], [{"description": "Portfolio"}])
    ).result

    assert {(str(r.date), r.portfolio): r.value for r in result} == {
        ("2020-01-31", "Lo 30"): 1.0,
        ("2020-02-29", "Lo 30"): None,
        ("2020-03-31", "Lo 30"): 3.0,
        ("2020-01-31", "Hi 30"): None,
        ("2020-02-29", "Hi 30"): 2.0,
        ("2020-03-31", "Hi 30"): None,
    }


@pytest.mark.parametrize(("fetcher", "query_cls"), PORTFOLIO_FETCHERS)
def test_portfolio_transform_data_number_of_firms_missing_values(fetcher, query_cls):
    frame = DataFrame({"Lo 30": ["10", "-999", "-99.99"]}, index=DATES)
    frame.index.name = "Date"

    result = fetcher.transform_data(
        query_cls(measure="number_of_firms"), ([frame], [{"description": "Portfolio"}])
    ).result

    assert [r.value for r in result] == [10, None, None]
    assert isinstance(result[0].value, int)


@pytest.mark.parametrize(("fetcher", "query_cls"), INTERNATIONAL_FETCHERS)
def test_international_transform_data_missing_values(fetcher, query_cls):
    frame = DataFrame(
        {
            "Date": DATES,
            "Mkt": ["1.0", "-99.99", "3.0"],
            "High": ["0.5", "-99.99", "-999"],
            "Low": ["-99.99", "0.2", "0.3"],
        }
    ).set_index(["Date", "Mkt"])
    frame.columns = MultiIndex.from_arrays([["BE/ME", "BE/ME"], ["High", "Low"]])

    result = fetcher.transform_data(
        query_cls(measure="usd"), ([frame], [{"description": "Index"}])
    ).result

    assert [r.mkt for r in result] == [1.0, None, 3.0]
    assert [r.be_me_high for r in result] == [0.5, None, None]
    assert [r.be_me_low for r in result] == [None, 0.2, 0.3]
