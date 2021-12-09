```text
usage: load [-t S_TICKER] [-s S_START_DATE] [-e S_END_DATE] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p] [-h]
```
Load a ticker to see its industry and sector classification. 

```
optional arguments:
  -t S_TICKER, --ticker S_TICKER
                        Stock ticker (default: None)
  -s S_START_DATE, --start S_START_DATE
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-12-04)
  -e S_END_DATE, --end S_END_DATE
                        The ending date (format YYYY-MM-DD) of the stock (default: 2021-12-05)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  --source {yf,av,iex}  Source of historical data. (default: yf)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -h, --help            show this help message (default: False)
```

Sample output: 

```
(✨) (stocks)>(sia)> load gm
Loading Daily GM stock with starting period 2020-12-04 for analysis.

(✨) (stocks)>(sia)> help

Sector and Industry Analysis:
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to main menu
    quit          quit to abandon program
    load          load a ticker and get its industry, sector, country and market cap

    clear         clear all or one of industry, sector, country and market cap parameters
    industry      see existing industries, or set industry if arg specified
    sector        see existing sectors, or set sector if arg specified
    country       see existing countries, or set country if arg specified
    mktcap        set mktcap between small, mid or large
    exchange      revert exclude international exchanges flag

Industry          : Auto Manufacturers
Sector            : Consumer Cyclical
Country           : United States
Market Cap        : Large
Exclude Exchanges : True

Country (and Market Cap)
    cpi           companies per industry in country
    cps           companies per sector in country

Financials 
    roa           return on assets
    roe           return on equity
    cr            current ratio
    qr            quick ratio
    de            debt to equity
    tc            total cash
    tcs           total cash per share
    tr            total revenue
    rps           revenue per share
    rg            revenue growth
    eg            earnings growth
    pm            profit margins
    gp            gross profits
    gm            gross margins
    ocf           operating cash flow
    om            operating margins
    fcf           free cash flow
    td            total debt
    ebitda        earnings before interest, taxes, depreciation and amortization
    ebitdam       ebitda margins
    rec           recommendation mean

Returned tickers: 
>   ca            take these to comparison analysis menu
```
