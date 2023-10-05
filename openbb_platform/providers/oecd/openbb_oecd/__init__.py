"""FRED provider module."""
from openbb_oecd.models.gdpnom import OECDGDPNomFetcher

from openbb_provider.abstract.provider import Provider

oecd_provider = Provider(
    name="oecd",
    website="https://stats.oecd.org/",
    description="""OECD""",
    fetcher_dict={
        "GDPNom": OECDGDPNomFetcher,
    },
)
