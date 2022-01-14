import pytest

from gamestonk_terminal.cryptocurrency.defi import llama_view


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_protocols():
    llama_view.display_defi_protocols(20, "tvl", False, False)


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_tvl(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=llama_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")
    llama_view.display_defi_tvl(20)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_grouped_defi_protocols(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=llama_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")
    llama_view.display_grouped_defi_protocols(20)


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical_tvl(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=llama_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")
    llama_view.display_historical_tvl("sushiswap,uniswap")
