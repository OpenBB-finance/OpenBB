# IMPORTATION STANDARD

from datetime import datetime

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.fundamental_analysis import business_insider_view
from openbb_terminal.stocks.stocks_helper import load


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
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_management(mocker, use_tab):
    preferences = PreferencesModel(USE_TABULATE_DF=use_tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    business_insider_view.display_management(symbol="TSLA", export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_management_nodata():
    business_insider_view.display_management(symbol="GH", export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_raw():
    business_insider_view.display_price_target_from_analysts(
        symbol="TSLA",
        start_date=None,
        data=None,
        limit=None,
        raw=True,
        export=None,
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_price_target_from_analysts_plt():
    ticker = "TSLA"
    interval = 1440
    start = datetime.strptime("2021-12-05", "%Y-%m-%d")
    stock = load(symbol=ticker, start_date=start, interval=interval)

    business_insider_view.display_price_target_from_analysts(
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
    business_insider_view.display_estimates(
        symbol="TSLA", estimate="annual_earnings", export=None
    )
