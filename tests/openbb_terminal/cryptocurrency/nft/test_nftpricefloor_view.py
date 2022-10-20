import pytest

from openbb_terminal.cryptocurrency.nft import nftpricefloor_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_floor_price():
    nftpricefloor_view.display_floor_price("cryptopunks")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_collections():
    nftpricefloor_view.display_collections()
