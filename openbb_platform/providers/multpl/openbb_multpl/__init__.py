"""Multpl Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_multpl.models.sp500_multiples import MultplSP500MultiplesFetcher

multpl_provider = Provider(
    name="multpl",
    website="https://www.multpl.com/",
    description="""Public broad-market data published to https://multpl.com.""",
    fetcher_dict={
        "SP500Multiples": MultplSP500MultiplesFetcher,
    },
)
