# OpenBB Nasdaq Provider

This extension integrates the [Nasdaq](https://www.nasdaq.com) data provider into the OpenBB Platform.

## Installation

To install the extension:

```bash
pip install openbb-nasdaq
```

## Coverage

The following endpoints are covered by this extension:

- `obb.economy.calendar`
- `obb.equity.calendar.dividend`
- `obb.equity.calendar.earnings`
- `obb.equity.calendar.ipo`
- `obb.equity.search`
- `obb.equity.screener`
- `obb.equity.fundamental.dividend`
- `obb.equity.fundamental.filings`

Router extensions are required (`openbb-economy` & `openbb-equity`) to populate endpoints, but fetchers can be used independent of the Python and API interfaces.

```python
from openbb_nasdaq import nasdaq_provider

nasdaq_provider.fetcher_dict
```

```python
{'CalendarDividend': openbb_nasdaq.models.calendar_dividend.NasdaqCalendarDividendFetcher,
'CalendarEarnings': openbb_nasdaq.models.calendar_earnings.NasdaqCalendarEarningsFetcher,
'CalendarIpo': openbb_nasdaq.models.calendar_ipo.NasdaqCalendarIpoFetcher,
'CompanyFilings': openbb_nasdaq.models.company_filings.NasdaqCompanyFilingsFetcher,
'EconomicCalendar': openbb_nasdaq.models.economic_calendar.NasdaqEconomicCalendarFetcher,
'EquitySearch': openbb_nasdaq.models.equity_search.NasdaqEquitySearchFetcher,
'EquityScreener': openbb_nasdaq.models.equity_screener.NasdaqEquityScreenerFetcher,
'HistoricalDividends': openbb_nasdaq.models.historical_dividends.NasdaqHistoricalDividendsFetcher,
'TopRetail': openbb_nasdaq.models.top_retail.NasdaqTopRetailFetcher}
```

## OpenBB Workspace App

This package includes a standalone Workspace application for viewing market calendars and company filings.

Launch it from the command line, with the environment active, by entering:

```sh
openbb-api --app openbb_nasdaq.app:main --factory
```

This will start the FastAPI application via Uvicorn and serve the configuration files to Workspace when added as a backend data source.

To see all the launch arguments, use:

```sh
openbb-api --help
```

The application is served by a factory function, and the FastAPI instance can be utilized by calling the `main` function.

```python
from openbb_nasdaq.app import main

app = main()
```

## OpenBB Documentation

OpenBB Platform documentation is available [here](https://docs.openbb.co/platform).

OpenBB Workspace documentation is available [here](https://docs.openbb.co/workspace).
