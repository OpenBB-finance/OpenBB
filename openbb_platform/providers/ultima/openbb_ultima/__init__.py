"""Ultima provider module."""
from openbb_provider.abstract.provider import Provider
from openbb_ultima.models.stock_news import UltimaStockNewsFetcher

ultima_provider = Provider(
    name="ultima",
    website="https://www.ultimainsights.ai/openbb",
    description="""Ultima harnesses the power of LLMs to deliver news before it hits the frontpage of Bloomberg.""",
    required_credentials=["api_key"],
    fetcher_dict={
        "StockNews": UltimaStockNewsFetcher,
    },
)
