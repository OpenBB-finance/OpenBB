"""Banxico provider module."""

from openbb_banxico.models.currency_historical import (
    BanxicoCurrencyHistoricalFetcher,
)
from openbb_core.provider.abstract.provider import Provider

banxico_provider = Provider(
    name="banxico",
    website="https://www.banxico.org.mx/SieAPIRest/service/v1/",
    description=(
        "Banco de México's Economic Information System (SIE) publishes Mexican economic and financial time series."
    ),
    credentials=["api_key"],
    fetcher_dict={"CurrencyHistorical": BanxicoCurrencyHistoricalFetcher},
    repr_name="Banco de México (Banxico)",
    instructions=(
        "Request a free SIE API token from Banco de México, then configure it as the `banxico_api_key` credential."
    ),
)
