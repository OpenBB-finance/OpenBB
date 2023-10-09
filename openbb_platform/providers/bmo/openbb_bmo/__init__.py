"""BMO provider module."""

from openbb_bmo.models.etf_countries import BmoEtfCountriesFetcher
from openbb_bmo.models.etf_historical_nav import BmoEtfHistoricalNavFetcher
from openbb_bmo.models.etf_holdings import BmoEtfHoldingsFetcher
from openbb_bmo.models.etf_info import BmoEtfInfoFetcher
from openbb_bmo.models.etf_search import BmoEtfSearchFetcher
from openbb_bmo.models.etf_sectors import BmoEtfSectorsFetcher
from openbb_provider.abstract.provider import Provider

bmo_provider = Provider(
    name="bmo",
    website="https://www.bmogam.com",
    description="""BMO is a major Canadian bank  and issuer of ETFs.""",
    required_credentials=None,
    fetcher_dict={
        "EtfCountries": BmoEtfCountriesFetcher,
        "EtfHistoricalNav": BmoEtfHistoricalNavFetcher,
        "EtfHoldings": BmoEtfHoldingsFetcher,
        "EtfInfo": BmoEtfInfoFetcher,
        "EtfSearch": BmoEtfSearchFetcher,
        "EtfSectors": BmoEtfSectorsFetcher,
    },
)
