"""OECD provider module."""

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

oecd_provider = Provider(
    name="oecd",
    website="https://data-explorer.oecd.org/",
    description="""Access OECD data via the SDMX REST API.
Covers all OECD dataflows including GDP, CPI, unemployment,
interest rates, and hundreds more.""",
    fetcher_dict={
        # Generic fetchers
        "AvailableIndicators": OecdAvailableIndicatorsFetcher,
        "EconomicIndicators": OecdEconomicIndicatorsFetcher,
        # Specialized fetchers
        "BalanceOfPayments": OECDBalanceOfPaymentsFetcher,
        "CompositeLeadingIndicator": OECDCompositeLeadingIndicatorFetcher,
        "ConsumerPriceIndex": OECDCPIFetcher,
        "CountryInterestRates": OecdCountryInterestRatesFetcher,
        "GdpNominal": OECDGdpNominalFetcher,
        "GdpReal": OECDGdpRealFetcher,
        "GdpForecast": OECDGdpForecastFetcher,
        "HousePriceIndex": OECDHousePriceIndexFetcher,
        "SharePriceIndex": OECDSharePriceIndexFetcher,
        "Unemployment": OECDUnemploymentFetcher,
    },
    repr_name="Organization for Economic Co-operation and Development (OECD)",
)
