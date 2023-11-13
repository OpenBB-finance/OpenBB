"""Benzinga provider module."""
from openbb_benzinga.models.company_news import BenzingaCompanyNewsFetcher
from openbb_benzinga.models.global_news import BenzingaGlobalNewsFetcher
from openbb_provider.abstract.provider import Provider

benzinga_provider = Provider(
    name="benzinga",
    website="https://www.benzinga.com/",
    description="""Benzinga is a financial data provider that offers an API
    focused on information that moves the market.""",
    required_credentials=["api_key"],
    fetcher_dict={
        "CompanyNews": BenzingaCompanyNewsFetcher,
        "GlobalNews": BenzingaGlobalNewsFetcher,
    },
)
