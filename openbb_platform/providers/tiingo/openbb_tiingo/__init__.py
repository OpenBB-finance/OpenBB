"""Tiingo provider module."""


from openbb_provider.abstract.provider import Provider

tiingo_provider = Provider(
    name="tiingo",
    website="https://tiingo.com/",
    description="""""",
    required_credentials=["token"],
    fetcher_dict={},
)
