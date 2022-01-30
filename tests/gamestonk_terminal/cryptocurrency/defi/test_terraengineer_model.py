# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
import pytest

# IMPORTATION INTERNAL
from gamestonk_terminal.cryptocurrency.defi import terraengineer_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "asset,address",
    [("ust", "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8")],
)
def test_get_history_asset_from_terra_address(asset, address, recorder):
    df = terraengineer_model.get_history_asset_from_terra_address(
        asset=asset,
        address=address,
    )
    recorder.capture(df)


@pytest.mark.vcr(record_mode="none")
def test_get_history_asset_from_terra_address_status_400(mocker):
    # MOCK GET
    attrs = {
        "status_code": 400,
    }
    mock_response = mocker.Mock(**attrs)
    mocker.patch(target="requests.get", new=mocker.Mock(return_value=mock_response))

    with pytest.raises(Exception) as _:
        terraengineer_model.get_history_asset_from_terra_address(
            asset="ust",
            address="terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8",
        )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "asset, address",
    [
        ("ust", "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"),
        ("WRONG_ASSET", "terra1tmnqgvg567ypvsvk6rwsga3srp7e3lg6u0elp8"),
        ("ust", "WRONG_ADDRESS"),
    ],
)
def test_get_history_asset_from_terra_address_wrong_param(asset, address):
    with pytest.raises(Exception) as _:
        terraengineer_model.get_history_asset_from_terra_address(
            asset=asset,
            address=address,
        )
