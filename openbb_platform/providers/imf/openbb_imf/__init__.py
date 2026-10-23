"""OpenBB IMF Provider Module."""

from __future__ import annotations

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_imf.models.available_indicators import ImfAvailableIndicatorsFetcher
from openbb_imf.models.balance_of_payments import ImfBalanceOfPaymentsFetcher
from openbb_imf.models.consumer_price_index import ImfConsumerPriceIndexFetcher
from openbb_imf.models.container_metrics import ImfContainerMetricsFetcher
from openbb_imf.models.country_activity import ImfCountryActivityFetcher
from openbb_imf.models.direction_of_trade import ImfDirectionOfTradeFetcher
from openbb_imf.models.disruption_events import ImfDisruptionEventsFetcher
from openbb_imf.models.disruption_sankey import ImfDisruptionSankeyFetcher
from openbb_imf.models.economic_indicators import ImfEconomicIndicatorsFetcher
from openbb_imf.models.maritime_chokepoint_info import ImfMaritimeChokePointInfoFetcher
from openbb_imf.models.maritime_chokepoint_volume import (
    ImfMaritimeChokePointVolumeFetcher,
)
from openbb_imf.models.monthly_trade import ImfMonthlyTradeFetcher
from openbb_imf.models.port_info import ImfPortInfoFetcher
from openbb_imf.models.port_volume import ImfPortVolumeFetcher

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None


def _key(standard: str, imf_alias: str) -> str:
    """Return the standard key when ``openbb-economy`` is installed, else the IMF alias."""
    return standard if ECONOMY_INSTALLED else imf_alias


imf_provider = Provider(
    name="imf",
    website="https://datahelp.imf.org/knowledgebase/articles/667681-using-json-restful-web-service",
    description="Access International Monetary Fund (IMF) data APIs.",
    fetcher_dict={
        _key("AvailableIndicators", "AvailableImfIndicators"): (
            ImfAvailableIndicatorsFetcher
        ),
        _key("BalanceOfPayments", "ImfBalanceOfPayments"): (
            ImfBalanceOfPaymentsFetcher
        ),
        _key("ConsumerPriceIndex", "ImfConsumerPriceIndex"): (
            ImfConsumerPriceIndexFetcher
        ),
        "ContainerMetrics": ImfContainerMetricsFetcher,
        "CountryActivity": ImfCountryActivityFetcher,
        _key("DirectionOfTrade", "ImfDirectionOfTrade"): ImfDirectionOfTradeFetcher,
        "DisruptionEvents": ImfDisruptionEventsFetcher,
        "DisruptionSankey": ImfDisruptionSankeyFetcher,
        _key("EconomicIndicators", "ImfIndicators"): ImfEconomicIndicatorsFetcher,
        _key("MaritimeChokePointInfo", "ImfMaritimeChokePointInfo"): (
            ImfMaritimeChokePointInfoFetcher
        ),
        _key("MaritimeChokePointVolume", "ImfMaritimeChokePointVolume"): (
            ImfMaritimeChokePointVolumeFetcher
        ),
        "MonthlyTrade": ImfMonthlyTradeFetcher,
        _key("PortInfo", "ImfPortInfo"): ImfPortInfoFetcher,
        _key("PortVolume", "ImfPortVolume"): ImfPortVolumeFetcher,
    },
    repr_name="International Monetary Fund (IMF) Data APIs",
)
