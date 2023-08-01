"""FRED provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_fred.models.cpi import FREDCPIFetcher

fred_provider = Provider(
    name="fred",
    website="https://fred.stlouisfed.org/",
    description="""Federal Reserve Economic Data is a database maintained by the
     Research division of the Federal Reserve Bank of St. Louis that has more than
     816,000 economic time series from various sources.""",
    required_credentials=["api_key"],
    fetcher_dict={"CPI": FREDCPIFetcher},
)
