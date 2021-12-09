# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import market_watch_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "quarter",
    [True, False],
)
def test_prepare_df_financials(quarter, recorder):
    result_df = market_watch_model.prepare_df_financials(
        ticker="AAPL", statement="income", quarter=quarter
    )

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_prepare_df_financials_wrong_statement():
    with pytest.raises(ValueError):
        market_watch_model.prepare_df_financials(
            ticker="AAPL",
            statement="INVALID_STATEMENT",
            quarter=False,
        )


@pytest.mark.vcr
@pytest.mark.parametrize(
    "debug",
    [True, False],
)
def test_pget_sean_seah_warnings(recorder, debug):
    result_df, _, _ = market_watch_model.get_sean_seah_warnings(
        ticker="AAPL",
        debug=debug,
    )

    recorder.capture(result_df)
