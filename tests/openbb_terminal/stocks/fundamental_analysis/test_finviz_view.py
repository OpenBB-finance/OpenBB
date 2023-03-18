# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

from openbb_terminal import helper_funcs

# IMPORTATION INTERNAL
from openbb_terminal.stocks.fundamental_analysis import finviz_view


@pytest.mark.vcr
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_screen_data(mocker, use_tab):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    mocker.patch.object(
        target=helper_funcs.obbff, attribute="USE_TABULATE_DF", new=use_tab
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
