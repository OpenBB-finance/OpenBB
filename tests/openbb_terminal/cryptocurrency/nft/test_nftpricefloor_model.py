import pytest

from openbb_terminal.cryptocurrency.nft import nftpricefloor_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "slug",
    [
        "cryptopunks",
    ],
)
def test_get_floor_price(slug, recorder):
    df_floor_price = nftpricefloor_model.get_floor_price(slug)
    recorder.capture(df_floor_price.head(1))


@pytest.mark.vcr
def test_get_collections(recorder):
    df = nftpricefloor_model.get_collections()
    recorder.capture(df)
