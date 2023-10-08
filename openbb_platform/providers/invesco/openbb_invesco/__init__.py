"""Invesco provider module."""

from openbb_provider.abstract.provider import Provider

from openbb_invesco.models.etf_holdings import InvescoEtfHoldingsFetcher
from openbb_invesco.models.etf_search import InvescoEtfSearchFetcher

invesco_provider = Provider(
    name="invesco",
    website="https://www.invesco.com/",
    description="""Invesco is a financial services company and issuer of Invesco ETFs.""",
    required_credentials=None,
    fetcher_dict={
        "EtfHoldings": InvescoEtfHoldingsFetcher,
        "EtfSearch": InvescoEtfSearchFetcher,
    },
)
