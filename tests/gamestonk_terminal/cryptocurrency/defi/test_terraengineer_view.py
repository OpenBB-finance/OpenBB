import pytest

from gamestonk_terminal.cryptocurrency.defi import terraengineer_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_anchor_yield_reserve(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=terraengineer_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    terraengineer_view.display_anchor_yield_reserve()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_terra_asset_history(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=terraengineer_view.gtff, attribute="USE_ION", new=True)
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="gamestonk_terminal.stocks.options.yfinance_view.plt.show")

    terraengineer_view.display_terra_asset_history(
        asset="ust", address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
    )
