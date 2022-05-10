```
usage: property [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
                [-f {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
                [-mt NAN_FILL_METHOD]
                [-pr {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}]
                [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
                [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL] [-v LONG_ALLOCATION]
                [--name NAME] [-h]
```

Returns a portfolio that is weighted based on selected property.

```
optional arguments:
  -p HISTORIC_PERIOD, --period HISTORIC_PERIOD
                        Period to get yfinance data from. Possible frequency
                        strings are: 'd': means days, for example '252d' means
                        252 days 'w': means weeks, for example '52w' means 52
                        weeks 'mo': means months, for example '12mo' means 12
                        months 'y': means years, for example '1y' means 1 year
                        'ytd': downloads data from beginning of year to today
                        'max': downloads all data available for each asset
                        (default: 3y)
  -s START_PERIOD, --start START_PERIOD
                        Start date to get yfinance data from. Must be in
                        'YYYY-MM-DD' format (default: )
  -e END_PERIOD, --end END_PERIOD
                        End date to get yfinance data from. Must be in 'YYYY-
                        MM-DD' format (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns. Possible values
                        are: 'd': for daily returns 'w': for weekly returns
                        'm': for monthly returns (default: d)
  -mn MAX_NAN, --maxnan MAX_NAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD_VALUE, --threshold THRESHOLD_VALUE
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt NAN_FILL_METHOD, --method NAN_FILL_METHOD
                        Method used to fill nan values in time series, by
                        default time. Possible values are: 'linear': linear
                        interpolation 'time': linear interpolation based on
                        time index 'nearest': use nearest value to replace nan
                        values 'zero': spline of zeroth order 'slinear':
                        spline of first order 'quadratic': spline of second
                        order 'cubic': spline of third order 'barycentric':
                        builds a polynomial that pass for all points (default:
                        time)
  -pr {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}, --property {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}
                        Property info to weight. Use one of yfinance info
                        options. (default: None)
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}
                        Risk measure used to optimize the portfolio. Possible
                        values are: 'MV' : Variance 'MAD' : Mean Absolute
                        Deviation 'MSV' : Semi Variance (Variance of negative
                        returns) 'FLPM' : First Lower Partial Moment 'SLPM' :
                        Second Lower Partial Moment 'CVaR' : Conditional Value
                        at Risk 'EVaR' : Entropic Value at Risk 'WR' : Worst
                        Realization 'ADD' : Average Drawdown of uncompounded
                        returns 'UCI' : Ulcer Index of uncompounded returns
                        'CDaR' : Conditional Drawdown at Risk of uncompounded
                        returns 'EDaR' : Entropic Drawdown at Risk of
                        uncompounded returns 'MDD' : Maximum Drawdown of
                        uncompounded returns (default: MV)
  -r RISK_FREE, --risk-free-rate RISK_FREE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -a SIGNIFICANCE_LEVEL, --alpha SIGNIFICANCE_LEVEL
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio (default: 1)
  --name NAME           Save portfolio with personalized or default name
                        (default: PROPERTY_0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 15:02 (🦋) /portfolio/po/ $ property -pr trailingEps

 [3 Years] Weighted Portfolio based on trailingEps

     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  6.36 % │
├──────┼─────────┤
│ AMZN │ 68.58 % │
├──────┼─────────┤
│ BA   │ -7.56 % │
├──────┼─────────┤
│ FB   │ 14.57 % │
├──────┼─────────┤
│ MSFT │  9.93 % │
├──────┼─────────┤
│ T    │  2.92 % │
├──────┼─────────┤
│ TSLA │  5.18 % │
└──────┴─────────┘

Annual (by 252) expected return: 33.74%
Annual (by √252) volatility: 30.25%
Sharpe ratio: 1.1094
```