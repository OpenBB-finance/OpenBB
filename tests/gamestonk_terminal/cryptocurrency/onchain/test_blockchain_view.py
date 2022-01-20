import pytest

from gamestonk_terminal.cryptocurrency.onchain import blockchain_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_circulating_supply(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=blockchain_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")
    blockchain_view.display_btc_circulating_supply(1_601_596_800, 1_641_573_787, "")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_btc_confirmed_transactions(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=blockchain_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")
    blockchain_view.display_btc_confirmed_transactions(1_601_596_800, 1_641_573_787, "")
