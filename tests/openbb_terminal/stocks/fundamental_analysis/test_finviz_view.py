# IMPORTATION STANDARD


# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    PreferencesModel,
    copy_user,
)
from openbb_terminal.stocks.fundamental_analysis import finviz_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_screen_data(mocker, use_tab):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    preferences = PreferencesModel(USE_TABULATE_DF=use_tab)
    mock_current_user = copy_user(preferences=preferences)
    mocker.patch(
        target="openbb_terminal.core.session.current_user.__current_user",
        new=mock_current_user,
    )
    finviz_view.display_screen_data(symbol="AAPL", export="")


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "val, expected",
    [
        ("RANDOM_VALUE", "RANDOM_VALUE"),
        ("Upgrade", "[green]Upgrade[/green]"),
        ("Downgrade", "[red]Downgrade[/red]"),
        ("Reiterated", "[yellow]Reiterated[/yellow]"),
    ],
)
def test_lambda_category_color_red_green(val, expected):
    result = finviz_view.lambda_category_color_red_green(val=val)
    assert result == expected
