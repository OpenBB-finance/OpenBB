"""stockgrid provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_stockgrid.models.short_volume import StockgridShortVolumeFetcher

stockgrid_provider = Provider(
    name="stockgrid",
    website="www.stockgrid.io",
    description=(
        "Stockgrid gives you a detailed view of what smart money is doing. "
        "Get in depth data about large option blocks being traded, including "
        "the sentiment score, size, volume and order type. Stop guessing and "
        "build a strategy around the number 1 factor moving the market: money."
    ),
    fetcher_dict={
        "ShortVolume": StockgridShortVolumeFetcher,
    },
)
