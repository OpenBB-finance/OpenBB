# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import nasdaq_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, limit, year, form_group",
    [
        ("TSLA", 5, 2020, "annual"),
    ],
)
def test_get_sec_filings(symbol, limit, year, form_group):
    result_df = nasdaq_model.get_sec_filings(
        symbol=symbol, limit=limit, year=year, form_group=form_group
    )
    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.vcr
def test_get_rating_over_time(recorder):
    result_df = nasdaq_model.get_sec_filings(
        symbol="TSLA", year=2020, form_group="annual"
    )
    recorder.capture(result_df)
