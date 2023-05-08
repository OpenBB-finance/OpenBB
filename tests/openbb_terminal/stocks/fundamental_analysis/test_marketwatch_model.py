# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest
from pandas import DataFrame

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import marketwatch_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [("token", "MOCK_TOKEN")],
    }


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, statement, quarter",
    [
        ("TSLA", "income", False),
        ("TSLA", "balance", False),
        ("TSLA", "cashflow", False),
    ],
)
def test_prepare_df_financials(symbol, statement, quarter):
    result_df = marketwatch_model.prepare_df_financials(
        symbol=symbol, statement=statement, quarter=quarter
    )
    assert isinstance(result_df, DataFrame)
    assert not result_df.empty


@pytest.mark.record_http
@pytest.mark.parametrize(
    "symbol, debug",
    [
        ("TSLA", False),
    ],
)
def test_get_sean_seah_warnings(symbol, debug):
    result_df = marketwatch_model.get_sean_seah_warnings(symbol=symbol, debug=debug)
    assert isinstance(result_df[0], DataFrame)
    assert not result_df[0].empty
