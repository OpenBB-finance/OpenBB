"""BIS Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_bis.models.house_price_index import BISHousePriceIndexFetcher

bis_provider = Provider(
    name="bis",
    website="https://data.bis.org",
    description=(
        "BIS Data Portal."
    ),
    fetcher_dict={
        "HousePriceIndex": BISHousePriceIndexFetcher,
    },
    repr_name="Bank for International Settlements",
)
