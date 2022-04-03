# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.government import quiverquant_model


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("Authorization", "MOCK_TOKEN")],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "gov_type, ticker",
    [
        # ("congress", None),
        ("congress", "COIN"),
        # ("senate", None),
        ("senate", "CONE"),
        # ("house", None),
        ("house", "SPY"),
        # ("contracts", None),
        ("contracts", "AMRC"),
        # ("quarter-contracts", None),
        ("quarter-contracts", "SSTK"),
        # ("corporate-lobbying", None),
        ("corporate-lobbying", "HBI"),
    ],
)
def test_get_government_trading(gov_type, recorder, ticker):
    result_df = quiverquant_model.get_government_trading(
        gov_type=gov_type,
        ticker=ticker,
    )
    recorder.capture(result_df.head(10))


@pytest.mark.default_cassette("test_analyze_qtr_contracts")
@pytest.mark.vcr
@pytest.mark.parametrize("analysis", ["total", "upmom", "downmom"])
def test_analyze_qtr_contracts(analysis, recorder):
    result_df = quiverquant_model.analyze_qtr_contracts(
        analysis=analysis,
        num=10,
    )
    recorder.capture(result_df.head(10))
