"""EconDB provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_econdb.models.available_indicators import EconDbAvailableIndicatorsFetcher
from openbb_econdb.models.country_profile import EconDbCountryProfileFetcher
from openbb_econdb.models.economic_indicators import EconDbEconomicIndicatorsFetcher
from openbb_econdb.models.export_destinations import EconDbExportDestinationsFetcher
from openbb_econdb.models.gdp_nominal import EconDbGdpNominalFetcher
from openbb_econdb.models.gdp_real import EconDbGdpRealFetcher
from openbb_econdb.models.port_volume import EconDbPortVolumeFetcher
from openbb_econdb.models.yield_curve import EconDbYieldCurveFetcher

econdb_provider = Provider(
    name="EconDB",
    website="https://econdb.com",
    description="""The mission of the company is to process information in ways that
facilitate understanding of the economic situation at different granularity levels.

The sources of data include official statistics agencies and so-called alternative
data sources where we collect direct observations of the market and generate
aggregate statistics.""",
    credentials=[
        "api_key"
    ],  # Can be left as None, an attempt to use a temporary token will be made.
    fetcher_dict={
        "AvailableIndicators": EconDbAvailableIndicatorsFetcher,
        "CountryProfile": EconDbCountryProfileFetcher,
        "EconomicIndicators": EconDbEconomicIndicatorsFetcher,
        "ExportDestinations": EconDbExportDestinationsFetcher,
        "GdpNominal": EconDbGdpNominalFetcher,
        "GdpReal": EconDbGdpRealFetcher,
        "PortVolume": EconDbPortVolumeFetcher,
        "YieldCurve": EconDbYieldCurveFetcher,
    },
    repr_name="EconDB",
)
