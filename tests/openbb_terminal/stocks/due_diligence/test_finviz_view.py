# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.stocks.due_diligence import finviz_view


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


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_news(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    finviz_view.news(ticker="TSLA", num=5)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_analyst(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})
    finviz_view.analyst(ticker="TSLA", export=None)
