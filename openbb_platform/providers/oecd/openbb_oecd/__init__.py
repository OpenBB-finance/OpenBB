"""OECD provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_oecd.models.composite_leading_indicator import OECDCLIFetcher
from openbb_oecd.models.consumer_price_index import OECDCPIFetcher
from openbb_oecd.models.gdp_forecast import OECDGdpForecastFetcher
from openbb_oecd.models.gdp_nominal import OECDGdpNominalFetcher
from openbb_oecd.models.gdp_real import OECDGdpRealFetcher
from openbb_oecd.models.house_price_index import OECDHousePriceIndexFetcher
from openbb_oecd.models.immediate_interest_rate import OECDImmediateInterestRateFetcher
from openbb_oecd.models.long_term_interest_rate import OECDLTIRFetcher
from openbb_oecd.models.share_price_index import OECDSharePriceIndexFetcher
from openbb_oecd.models.short_term_interest_rate import OECDSTIRFetcher
from openbb_oecd.models.unemployment import OECDUnemploymentFetcher

oecd_provider = Provider(
    name="oecd",
    website="https://data-explorer.oecd.org/",
    description="""OECD Data Explorer includes data and metadata for OECD countries and selected
non-member economies.""",
    fetcher_dict={
        "GdpNominal": OECDGdpNominalFetcher,
        "GdpReal": OECDGdpRealFetcher,
        "GdpForecast": OECDGdpForecastFetcher,
        "HousePriceIndex": OECDHousePriceIndexFetcher,
        "ImmediateInterestRate": OECDImmediateInterestRateFetcher,
        "Unemployment": OECDUnemploymentFetcher,
        "CLI": OECDCLIFetcher,
        "SharePriceIndex": OECDSharePriceIndexFetcher,
        "STIR": OECDSTIRFetcher,
        "LTIR": OECDLTIRFetcher,
        "ConsumerPriceIndex": OECDCPIFetcher,
    },
    repr_name="Organization for Economic Co-operation and Development (OECD)",
)
