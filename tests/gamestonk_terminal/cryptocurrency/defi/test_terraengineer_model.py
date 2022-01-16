import pytest

from gamestonk_terminal.cryptocurrency.defi import terraengineer_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "asset,address",
    [("ust", "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8")],
)
def test_get_history_asset_from_terra_address(asset, address, recorder):
    df = terraengineer_model.get_history_asset_from_terra_address(
        asset=asset, address=address
    )
    recorder.capture(df)
