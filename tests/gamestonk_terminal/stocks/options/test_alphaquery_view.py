# IMPORTATION STANDARD
from datetime import datetime

# IMPORTATION THIRDPARTY
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.options import alphaquery_view


@pytest.mark.vcr
def test_display_put_call_ratio(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=alphaquery_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.backtesting.bt_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.backtesting.bt_view.plt.show")

    alphaquery_view.display_put_call_ratio(
        ticker="PM",
        window=10,
        start_date=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        export="",
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_display_put_call_ratio_empty(mocker):
    mocker.patch(
        target="gamestonk_terminal.stocks.options.alphaquery_view.alphaquery_model.get_put_call_ratio",
        return_value=pd.DataFrame(),
    )
    alphaquery_view.display_put_call_ratio(
        ticker="PM",
        window=10,
        start_date=datetime.strptime("2021-12-01", "%Y-%m-%d"),
        export="",
    )
