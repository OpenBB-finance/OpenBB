import pytest

from openbb_terminal.cryptocurrency.nft import opensea_model


@pytest.mark.vcr
@pytest.mark.parametrize(
    "slug",
    [
        "mutant-ape-yacht-club",
        "cryptopunks",
        "alien-frens",
    ],
)
def test_get_collection_stats(slug, recorder):
    df_collection_stats = opensea_model.get_collection_stats(slug)
    recorder.capture(df_collection_stats)
