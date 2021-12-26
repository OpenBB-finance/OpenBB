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


@pytest.mark.default_cassette("test_display_income_comparison")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_display_income_comparison(mocker, tab):
    mocker.patch.object(
        target=marketwatch_view.gtff,
        attribute="USE_COLOR",
        new=True,
    )
    mocker.patch.object(
        target=marketwatch_view.gtff, attribute="USE_TABULATE_DF", new=tab
    )
    marketwatch_view.display_income_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )


@pytest.mark.default_cassette("test_display_balance_comparison")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_display_balance_comparison(mocker, tab):
    mocker.patch.object(
        target=marketwatch_view.gtff,
        attribute="USE_COLOR",
        new=True,
    )
    mocker.patch.object(
        target=marketwatch_view.gtff, attribute="USE_TABULATE_DF", new=tab
    )
    marketwatch_view.display_balance_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )


@pytest.mark.default_cassette("test_display_cashflow_comparison")
@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "tab",
    [True, False],
)
def test_display_cashflow_comparison(mocker, tab):
    mocker.patch.object(
        target=marketwatch_view.gtff,
        attribute="USE_COLOR",
        new=True,
    )
    mocker.patch.object(
        target=marketwatch_view.gtff, attribute="USE_TABULATE_DF", new=tab
    )
    marketwatch_view.display_cashflow_comparison(
        similar=["TSLA", "GM"],
        timeframe="31-Dec-2020",
        quarter=True,
        export="",
    )
