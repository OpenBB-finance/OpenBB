```
usage: property [-p PROPERTY] [-v VALUE] [--pie] [-h]
```

Returns a portfolio that is weighted based on a selected property info

```
optional arguments:
  -p PROPERTY, --property PROPERTY
                        Property info to weigh. Use one of: previousClose, regularMarketOpen, twoHundredDayAverage, trailingAnnualDividendYield,
                        payoutRatio, volume24Hr, regularMarketDayHigh, navPrice, averageDailyVolume10Day, totalAssets, regularMarketPreviousClose,
                        fiftyDayAverage, trailingAnnualDividendRate, open, toCurrency, averageVolume10days, expireDate, yield, algorithm,
                        dividendRate, exDividendDate, beta, circulatingSupply, regularMarketDayLow, priceHint, currency, trailingPE,
                        regularMarketVolume, lastMarket, maxSupply, openInterest, marketCap, volumeAllCurrencies, strikePrice, averageVolume,
                        priceToSalesTrailing12Months, dayLow, ask, ytdReturn, askSize, volume, fiftyTwoWeekHigh, forwardPE, fromCurrency,
                        fiveYearAvgDividendYield, fiftyTwoWeekLow, bid, dividendYield, bidSize, dayHigh, annualHoldingsTurnover, enterpriseToRevenue,
                        beta3Year, profitMargins, enterpriseToEbitda, 52WeekChange, morningStarRiskRating, forwardEps, revenueQuarterlyGrowth,
                        sharesOutstanding, fundInceptionDate, annualReportExpenseRatio, bookValue, sharesShort, sharesPercentSharesOut, fundFamily,
                        lastFiscalYearEnd, heldPercentInstitutions, netIncomeToCommon, trailingEps, lastDividendValue, SandP52WeekChange,
                        priceToBook, heldPercentInsiders, shortRatio, sharesShortPreviousMonthDate, floatShares, enterpriseValue,
                        threeYearAverageReturn, lastSplitFactor, legalType, lastDividendDate, morningStarOverallRating, earningsQuarterlyGrowth,
                        pegRatio, lastCapGain, shortPercentOfFloat, sharesShortPriorMonth, impliedSharesOutstanding, fiveYearAverageReturn, and
                        regularMarketPrice. (default: None)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  -h, --help            show this help message (default: False)
```
