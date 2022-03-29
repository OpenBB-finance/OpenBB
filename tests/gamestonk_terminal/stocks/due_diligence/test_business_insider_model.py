# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.due_diligence import business_insider_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.default_cassette("test_get_price_target_from_analysts_TSLA")
@pytest.mark.vcr
def test_get_price_target_from_analysts(recorder):
    result_df = business_insider_model.get_price_target_from_analysts(ticker="TSLA")

    recorder.capture(result_df)


@pytest.mark.default_cassette("test_get_price_target_from_analysts_TSLA")
@pytest.mark.vcr
def test_get_estimates_year_estimates(recorder):
    df_year_estimates, _, _ = business_insider_model.get_estimates(ticker="TSLA")
    result_df = df_year_estimates

    recorder.capture(result_df)


@pytest.mark.default_cassette("test_get_price_target_from_analysts_TSLA")
@pytest.mark.vcr
def test_get_estimates_quarter_earnings(recorder):
    _, df_quarter_earnings, _ = business_insider_model.get_estimates(ticker="TSLA")
    result_df = df_quarter_earnings

    recorder.capture(result_df)


@pytest.mark.default_cassette("test_get_price_target_from_analysts_TSLA")
@pytest.mark.vcr
def test_get_estimates_quarter_revenues(recorder):
    _, _, df_quarter_revenues = business_insider_model.get_estimates(ticker="TSLA")
    result_df = df_quarter_revenues

    recorder.capture(result_df)
