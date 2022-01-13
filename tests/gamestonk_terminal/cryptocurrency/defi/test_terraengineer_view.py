import pytest

from gamestonk_terminal.cryptocurrency.defi import terraengineer_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_anchor_yield_reserve():
    terraengineer_view.display_anchor_yield_reserve()


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_terra_asset_history():
    terraengineer_view.display_terra_asset_history(
        asset="ust", address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"
    )
