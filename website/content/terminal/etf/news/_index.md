```
usage: news [-l LIMIT] [-d N_START_DATE] [-o] [-s SOURCES [SOURCES ...]] [-h]
```

Prints latest news about ETF, including date, title and web link. [Source: News API]

```
optional arguments:
  -l LIMIT, --limit LIMIT
                        Limit of latest news being printed.
  -d N_START_DATE, --date N_START_DATE
                        The starting date (format YYYY-MM-DD) to search articles from
  -o, --oldest          Show oldest articles first
  -s SOURCES [SOURCES ...], --sources SOURCES [SOURCES ...]
                        Show news only from the sources specified (e.g bbc yahoo.com)
  -h, --help            show this help message
```

Sample output:

```
18 news articles for iShares+Russell+2000+ETF were found since 2022-01-11

2022-01-18 18:38:25   First National Bank of South Miami Buys iShares Commodities Select Strategy ETF, Walmart Inc, ...
https://finance.yahoo.com/news/first-national-bank-south-miami-183825873.html 

2022-01-18 16:53:20   Stock Market Sinks As Techs, Financials Slide; 3 Energy Stocks Top Buy Points
https://www.investors.com/market-trend/stock-market-today/stock-market-slides-as-yields-keep-rising-3-stocks-in-energy-sector-top-buy-points/ 

2022-01-18 14:00:00   Vistra: Turning A Threat Into An Opportunity
https://seekingalpha.com/article/4480026-vistra-turning-a-threat-into-an-opportunity 

2022-01-18 11:17:44   Dow Jones Futures Fall, Techs Dive As Treasury Yield Hits 2-Year High; Apple, Qualcomm Near Buy Points
https://www.investors.com/market-trend/stock-market-today/dow-jones-futures-fall-techs-dive-treasury-yield-hits-2-year-high-apple-qualcomm-stock-near-buy-points/ 

2022-01-17 16:30:54   IYW: Technology Dashboard For January
https://seekingalpha.com/article/4479986-iyw-technology-dashboard-for-january 
```
