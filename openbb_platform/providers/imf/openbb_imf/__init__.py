"""OpenBB IMF Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.direction_of_trade import ImfDirectionOfTradeFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoFetcher
from openbb_imf.models.maritime_chokepoint_volume import (
    ImfMaritimeChokePointVolumeFetcher,
)
from openbb_imf.models.port_info import ImfPortInfoFetcher
from openbb_imf.models.port_volume import ImfPortVolumeFetcher

imf_provider = Provider(
    name="imf",
    website="https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service",
    description="Access International Monetary Fund (IMF) data APIs.",
    fetcher_dict={
        "AvailableIndicators": ImfAvailableIndicatorsFetcher,
        "DirectionOfTrade": ImfDirectionOfTradeFetcher,
        "EconomicIndicators": ImfEconomicIndicatorsFetcher,
        "MaritimeChokePointInfo": ImfMaritimeChokePointInfoFetcher,
        "MaritimeChokePointVolume": ImfMaritimeChokePointVolumeFetcher,
        "PortInfo": ImfPortInfoFetcher,
        "PortVolume": ImfPortVolumeFetcher,
    },
    repr_name="International Monetary Fund (IMF) Data APIs",
)
