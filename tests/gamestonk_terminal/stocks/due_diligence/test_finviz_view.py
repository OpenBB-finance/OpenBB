# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.due_diligence import finviz_view


@pytest.mark.parametrize(
    "val, expected",
    [
        ("RANDOM_VALUE", "RANDOM_VALUE"),
        ("Upgrade", "\x1b[32mUpgrade\x1b[0m"),
        ("Downgrade", "\x1b[31mDowngrade\x1b[0m"),
        ("Reiterated", "\x1b[33mReiterated\x1b[0m"),
    ],
)
def test_category_color_red_green(val, expected):
    result = finviz_view.category_color_red_green(val=val)
    assert result == expected


@pytest.mark.skip(reason="Broken function and unused yet.")
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_news():
    finviz_view.news(ticker="TSLA", num=5)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_analyst():
    finviz_view.analyst(ticker="TSLA", export=None)
