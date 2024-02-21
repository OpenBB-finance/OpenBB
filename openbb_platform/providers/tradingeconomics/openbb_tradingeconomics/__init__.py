"""Trading Economics provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_tradingeconomics.models.economic_calendar import TEEconomicCalendarFetcher
from openbb_tradingeconomics.models.market_historical import TEMarketHistoricalFetcher

tradingeconomics_provider = Provider(
    name="tradingeconomics",
    website="https://tradingeconomics.com/",
    description="""Trading Economics""",
    credentials=["api_key"],
    fetcher_dict={
        "EconomicCalendar": TEEconomicCalendarFetcher,
        "MarketHistorical": TEMarketHistoricalFetcher,
    },
)
