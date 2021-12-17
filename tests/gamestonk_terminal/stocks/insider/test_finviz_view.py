# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import finviz.main_func
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.insider import finviz_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_last_insider_activity(mocker):
    # REMOVE FINVIZ STOCK_PAGE CACHE
    mocker.patch.object(target=finviz.main_func, attribute="STOCK_PAGE", new={})

    finviz_view.last_insider_activity(ticker="TSLA", num=5, export="")
