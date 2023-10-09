"""FRED provider module."""
from openbb_oecd.models.gdpforecast import OECDGDPForecastFetcher
from openbb_oecd.models.gdpnom import OECDGDPNomFetcher
from openbb_oecd.models.gdpreal import OECDGDPRealFetcher
from openbb_provider.abstract.provider import Provider

oecd_provider = Provider(
    name="oecd",
    website="https://stats.oecd.org/",
    description="""OECD""",
    fetcher_dict={
        "GDPNom": OECDGDPNomFetcher,
        "GDPReal": OECDGDPRealFetcher,
        "GDPForecast": OECDGDPForecastFetcher,
    },
)
