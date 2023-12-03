"""Ultima provider module."""
from openbb_core.provider.abstract.provider import Provider
from openbb_ultima.models.company_news import UltimaCompanyNewsFetcher

ultima_provider = Provider(
    name="ultima",
    website="https://www.ultimainsights.ai/openbb",
    description="""Ultima harnesses the power of LLMs to deliver news before it hits the frontpage of Bloomberg.""",
    credentials=["api_key"],
    fetcher_dict={
        "CompanyNews": UltimaCompanyNewsFetcher,
    },
)
