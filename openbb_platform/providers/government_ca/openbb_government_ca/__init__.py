"""Government of Canada provider extension module."""

from openbb_core.provider.abstract.provider import Provider

government_ca_provider = Provider(
    name="government_ca",
    website="https://www150.statcan.gc.ca",
    description="""Canadian government data (Statistics Canada SDMX).
Public APIs; no credentials required.""",
    credentials=None,
    fetcher_dict={},
    repr_name="Government of Canada (Statistics Canada)",
)
