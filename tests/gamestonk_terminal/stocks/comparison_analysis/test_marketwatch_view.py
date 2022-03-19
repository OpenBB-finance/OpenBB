# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.comparison_analysis import marketwatch_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_income_comparison(mocker):
    mocker.patch.object(
        target=marketwatch_view.rich_config,
        attribute="USE_COLOR",
        new=True,
    )

    marketwatch_view.display_income_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_balance_comparison(mocker):
    mocker.patch.object(
        target=marketwatch_view.rich_config,
        attribute="USE_COLOR",
        new=True,
    )

    marketwatch_view.display_balance_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_cashflow_comparison(mocker):
    mocker.patch.object(
        target=marketwatch_view.rich_config,
        attribute="USE_COLOR",
        new=True,
    )
    marketwatch_view.display_cashflow_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )
