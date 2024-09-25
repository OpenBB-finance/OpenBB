"""OpenBB IMF Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.direction_of_trade import ImfDirectionOfTradeFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher

imf_provider = Provider(
    name="imf",
    website="https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service",
    description="This provider allows you to access International Monetary Fund data through the IMF Public Data API.",
    fetcher_dict={
        "AvailableIndicators": ImfAvailableIndicatorsFetcher,
        "DirectionOfTrade": ImfDirectionOfTradeFetcher,
        "EconomicIndicators": ImfEconomicIndicatorsFetcher,
    },
    repr_name="International Monetary Fund (IMF) Public Data API",
)
