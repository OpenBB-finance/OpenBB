"""FRED provider module."""
from openbb_oecd.models.gdp_forecast import OECDForecastGDPFetcher
from openbb_oecd.models.gdp_nominal import OECDNominalGDPFetcher
from openbb_oecd.models.gdp_real import OECDRealGDPFetcher
from openbb_provider.abstract.provider import Provider

oecd_provider = Provider(
    name="oecd",
    website="https://stats.oecd.org/",
    description="""OECD""",
    fetcher_dict={
        "NominalGDP": OECDNominalGDPFetcher,
        "RealGDP": OECDRealGDPFetcher,
        "ForecastGDP": OECDForecastGDPFetcher,
    },
)
