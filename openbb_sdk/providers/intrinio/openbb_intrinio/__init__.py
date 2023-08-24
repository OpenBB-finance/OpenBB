"""intrinio provider module."""


from openbb_provider.abstract.provider import Provider


intrinio_provider = Provider(
    name="intrinio",
    website="https://intrinio.com/",
    description="""Intrinio is a financial data platform that provides real-time and
    historical financial market data to businesses and developers through an API.""",
    required_credentials=["api_key"],
    fetcher_dict={},
)
