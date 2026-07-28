"""OECD provider module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_oecd.models.available_indicators import OecdAvailableIndicatorsFetcher
from openbb_oecd.models.balance_of_payments import OECDBalanceOfPaymentsFetcher
from openbb_oecd.models.composite_leading_indicator import (
    OECDCompositeLeadingIndicatorFetcher,
)
from openbb_oecd.models.consumer_price_index import OECDCPIFetcher
from openbb_oecd.models.country_interest_rates import OecdCountryInterestRatesFetcher
from openbb_oecd.models.economic_indicators import OecdEconomicIndicatorsFetcher
from openbb_oecd.models.gdp_forecast import OECDGdpForecastFetcher
from openbb_oecd.models.gdp_nominal import OECDGdpNominalFetcher
from openbb_oecd.models.gdp_real import OECDGdpRealFetcher
from openbb_oecd.models.house_price_index import OECDHousePriceIndexFetcher
from openbb_oecd.models.share_price_index import OECDSharePriceIndexFetcher
from openbb_oecd.models.unemployment import OECDUnemploymentFetcher

ECONOMY_INSTALLED = find_spec("openbb_economy") is not None


def _key(standard: str, oecd_alias: str) -> str:
    """Return the standard key when ``openbb-economy`` is installed, else the OECD alias."""
    return standard if ECONOMY_INSTALLED else oecd_alias


oecd_provider = Provider(
    name="oecd",
    website="https://data-explorer.oecd.org/",
    description="""Access OECD data via the SDMX REST API.
Covers all OECD dataflows including GDP, CPI, unemployment,
interest rates, and hundreds more.""",
    fetcher_dict={
        _key("AvailableIndicators", "AvailableOecdIndicators"): (
            OecdAvailableIndicatorsFetcher
        ),
        _key("EconomicIndicators", "OecdIndicators"): OecdEconomicIndicatorsFetcher,
        _key("BalanceOfPayments", "OecdBalanceOfPayments"): (
            OECDBalanceOfPaymentsFetcher
        ),
        _key("CompositeLeadingIndicator", "OecdCompositeLeadingIndicator"): (
            OECDCompositeLeadingIndicatorFetcher
        ),
        _key("ConsumerPriceIndex", "OecdConsumerPriceIndex"): OECDCPIFetcher,
        _key("CountryInterestRates", "OecdCountryInterestRates"): (
            OecdCountryInterestRatesFetcher
        ),
        _key("GdpNominal", "OecdGdpNominal"): OECDGdpNominalFetcher,
        _key("GdpReal", "OecdGdpReal"): OECDGdpRealFetcher,
        _key("GdpForecast", "OecdGdpForecast"): OECDGdpForecastFetcher,
        _key("HousePriceIndex", "OecdHousePriceIndex"): OECDHousePriceIndexFetcher,
        _key("SharePriceIndex", "OecdSharePriceIndex"): OECDSharePriceIndexFetcher,
        _key("Unemployment", "OecdUnemployment"): OECDUnemploymentFetcher,
    },
    repr_name="Organization for Economic Co-operation and Development (OECD)",
)
