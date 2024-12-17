"""OpenBB Deribit Provider Module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_deribit.models.options_chains import DeribitOptionsChainsFetcher

deribit_provider = Provider(
    name="deribit",
    website="https://deribit.com/",
    description="""Unofficial Python client for public data published by Deribit.""",
    credentials=None,
    fetcher_dict={"OptionsChains": DeribitOptionsChainsFetcher},
    repr_name="Deribit Public Data",
    instructions="This provider does not require any credentials and is not meant for trading.",
)
