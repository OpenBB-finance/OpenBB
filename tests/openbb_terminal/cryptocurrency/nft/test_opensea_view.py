import pytest

from openbb_terminal.cryptocurrency.nft import opensea_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_collection_stats():
    opensea_view.get_collection_stats("mutant-ape-yacht-club")
