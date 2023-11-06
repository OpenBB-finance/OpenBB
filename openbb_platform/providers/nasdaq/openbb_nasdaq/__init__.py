"""Nasdaq provider module."""
from openbb_nasdaq.models.calendar_dividend import NasdaqDividendCalendarFetcher
from openbb_nasdaq.models.calendar_ipo import NasdaqCalendarIpoFetcher
from openbb_nasdaq.models.economic_calendar import NasdaqEconomicCalendarFetcher
from openbb_provider.abstract.provider import Provider

nasdaq_provider = Provider(
    name="nasdaq",
    website="https://www.nasdaq.com",
    description="""Positioned at the nexus of technology and the capital markets, Nasdaq
provides premier platforms and services for global capital markets and beyond with
unmatched technology, insights and markets expertise.""",
    fetcher_dict={
        "CalendarDividend": NasdaqDividendCalendarFetcher,
        "CalendarIpo": NasdaqCalendarIpoFetcher,
        "EconomicCalendar": NasdaqEconomicCalendarFetcher,
    },
)
