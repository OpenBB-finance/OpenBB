"""yfinance (Yahoo!Finance) provider module."""
from openbb_provider.abstract.provider import Provider


yfinance_provider = Provider(
    name="yfinance",
    website="https://finance.yahoo.com/",
    description="""Yahoo! Finance is a web-based platform that offers financial news,
    data, and tools for investors and individuals interested in tracking and analyzing
    financial markets and assets.""",
    required_credentials=None,
    fetcher_dict={},
)
