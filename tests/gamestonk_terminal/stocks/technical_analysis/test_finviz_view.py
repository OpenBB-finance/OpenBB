# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.stocks.technical_analysis import finviz_view

# pylint: disable=E1101


@pytest.mark.vcr
def test_view(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=finviz_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finviz_view.plt.ion"
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finviz_view.plt.imshow"
    )
    mocker.patch(
        target="gamestonk_terminal.stocks.technical_analysis.finviz_view.plt.show"
    )

    finviz_view.view(ticker="PM")

    finviz_view.plt.ion.assert_called_once()
    finviz_view.plt.imshow.assert_called_once()
    finviz_view.plt.show.assert_called_once()
