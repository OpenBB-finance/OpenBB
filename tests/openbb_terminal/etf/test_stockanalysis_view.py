# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.etf import stockanalysis_view


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }


@pytest.mark.vcr()
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "symbol,use_tab",
    [
        ("ARKQ", True),
        ("ARKW", True),
        ("ARKQ", False),
        ("ARKW", False),
    ],
)
def test_view_overview(symbol, use_tab, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=use_tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    stockanalysis_view.view_overview(symbol)


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "symbol",
    [
        ("ARKQ"),
        ("ARKW"),
    ],
)
def test_view_holdings(symbol, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    stockanalysis_view.view_holdings(symbol, limit=5, export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "symbols",
    [
        ["ARKQ", "ARKF"],
        ["ARKW", "ARKK"],
    ],
)
def test_view_comparisons(symbols, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    stockanalysis_view.view_comparisons(symbols, export="")


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "name",
    [
        ("ARKQ"),
        ("ARKW"),
    ],
)
def test_display_etf_by_name(name, mocker):
    preferences = PreferencesModel(USE_TABULATE_DF=False)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    stockanalysis_view.display_etf_by_name(name, limit=5, export="")
