# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal import helper_funcs

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import business_insider_view
from openbb_terminal.stocks.stocks_helper import load


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_management(monkeypatch, use_tab):
    monkeypatch.setattr(helper_funcs.obbff, "USE_TABULATE_DF", use_tab)
    business_insider_view.display_management(symbol="TSLA", export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_management_nodata():
    business_insider_view.display_management(symbol="GH", export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_raw(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    business_insider_view.price_target_from_analysts(
        symbol="TSLA",
        start_date=None,
        data=None,
        limit=None,
        raw=True,
        export=None,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_plt(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

    ticker = "TSLA"
    interval = 1440
    start = datetime.strptime("2021-12-05", "%Y-%m-%d")
    stock = load(symbol=ticker, start_date=start, interval=interval)

    business_insider_view.price_target_from_analysts(
        symbol=ticker,
        start_date=start,
        data=stock,
        limit=None,
        raw=False,
        export=None,
        sheet_name=None,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_estimates():
    business_insider_view.estimates(
        symbol="TSLA", estimate="annualearnings", export=None
    )
