```
usage: property [-p PROPERTY] [-v VALUE] [--pie] [-h]
```

Suggests a weighting based on a targeted statistic.

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
Example:
```
2022 Feb 14, 11:22 (✨) /portfolio/po/ $ property -p trailingEps
      Weights
┌────────┬─────────┐
│        │ Value   │
├────────┼─────────┤
│ BNS.TO │ 12.63 % │
├────────┼─────────┤
│ BMO.TO │ 18.99 % │
├────────┼─────────┤
│ TD.TO  │ 12.66 % │
├────────┼─────────┤
│ CM.TO  │ 22.85 % │
├────────┼─────────┤
│ NA.TO  │ 14.70 % │
├────────┼─────────┤
│ RY.TO  │ 18.14 % │
└────────┴─────────┘
```

![property](https://user-images.githubusercontent.com/46355364/153903858-80e67d54-e2f7-46cc-8958-201b198db9e2.png)
