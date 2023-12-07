"""Benzinga provider module."""
from openbb_benzinga.models.company_news import BenzingaCompanyNewsFetcher
from openbb_benzinga.models.world_news import BenzingaWorldNewsFetcher
from openbb_core.provider.abstract.provider import Provider

benzinga_provider = Provider(
    name="benzinga",
    website="https://www.benzinga.com/",
    description="""Benzinga is a financial data provider that offers an API
    focused on information that moves the market.""",
    credentials=["api_key"],
    fetcher_dict={
        "CompanyNews": BenzingaCompanyNewsFetcher,
        "WorldNews": BenzingaWorldNewsFetcher,
    },
)
