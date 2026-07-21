"""OpenBB NSE Provider module."""

from openbb_core.provider.abstract.provider import Provider

from openbb_nse.models.index_constituents import NseIndexConstituentsFetcher

nse_provider = Provider(
    name="nse",
    website="https://www.niftyindices.com",
    description=(
        "Data for the National Stock Exchange of India (NSE), sourced from the official"
        " constituent files published by NSE Indices Limited. No API key is required."
    ),
    fetcher_dict={
        "IndexConstituents": NseIndexConstituentsFetcher,
    },
    repr_name="National Stock Exchange of India (NSE)",
)
