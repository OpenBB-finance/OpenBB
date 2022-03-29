# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import eclect_us_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "1598220000"),
            ("period2", "1635980400"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_analysis():
    eclect_us_view.display_analysis(ticker="AAPL")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_analysis_invalid(mocker):
    mocker.patch(
        target="openbb_terminal.stocks.fundamental_analysis.eclect_us_view.eclect_us_model.get_filings_analysis",
        return_value="",
    )
    eclect_us_view.display_analysis(ticker="AAPL")
