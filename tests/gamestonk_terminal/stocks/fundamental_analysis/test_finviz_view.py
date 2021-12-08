# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.fundamental_analysis import finviz_view


@pytest.mark.vcr
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "use_tab",
    [True, False],
)
def test_display_screen_data(monkeypatch, use_tab):
    monkeypatch.setattr(finviz_view.gtff, "USE_TABULATE_DF", use_tab)
    finviz_view.display_screen_data(ticker="TSLA", export="")
