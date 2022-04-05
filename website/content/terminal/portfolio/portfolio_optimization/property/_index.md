```
usage: property [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}]
                [-mn MAXNAN] [-th THRESHOLD] [-mt METHOD]
                [-pr {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}]
                [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
                [-r RISK_FREE_RATE] [-a ALPHA] [-v VALUE] [--pie] [--hist]
                [--dd] [--rc-chart] [--heat] [-h]```

Returns a portfolio that is weighted based on selected property.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from (default: 3y)
  -s START, --start START
                        Start date to get yfinance data from (default: )
  -e END, --end END     End date to get yfinance data from (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns (default: d)
  -mn MAXNAN, --maxnan MAXNAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD, --threshold THRESHOLD
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt METHOD, --method METHOD
                        Method used to fill nan values (default: time)
  -pr {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}, --property {previousClose,regularMarketOpen,twoHundredDayAverage,trailingAnnualDividendYield,payoutRatio,volume24Hr,regularMarketDayHigh,navPrice,averageDailyVolume10Day,totalAssets,regularMarketPreviousClose,fiftyDayAverage,trailingAnnualDividendRate,open,toCurrency,averageVolume10days,expireDate,yield,algorithm,dividendRate,exDividendDate,beta,circulatingSupply,regularMarketDayLow,priceHint,currency,trailingPE,regularMarketVolume,lastMarket,maxSupply,openInterest,marketCap,volumeAllCurrencies,strikePrice,averageVolume,priceToSalesTrailing12Months,dayLow,ask,ytdReturn,askSize,volume,fiftyTwoWeekHigh,forwardPE,fromCurrency,fiveYearAvgDividendYield,fiftyTwoWeekLow,bid,dividendYield,bidSize,dayHigh,annualHoldingsTurnover,enterpriseToRevenue,beta3Year,profitMargins,enterpriseToEbitda,52WeekChange,morningStarRiskRating,forwardEps,revenueQuarterlyGrowth,sharesOutstanding,fundInceptionDate,annualReportExpenseRatio,bookValue,sharesShort,sharesPercentSharesOut,heldPercentInstitutions,netIncomeToCommon,trailingEps,lastDividendValue,SandP52WeekChange,priceToBook,heldPercentInsiders,shortRatio,sharesShortPreviousMonthDate,floatShares,enterpriseValue,fundFamily,threeYearAverageReturn,lastSplitFactor,legalType,lastDividendDate,morningStarOverallRating,earningsQuarterlyGrowth,pegRatio,lastCapGain,shortPercentOfFloat,sharesShortPriorMonth,impliedSharesOutstanding,fiveYearAverageReturn,regularMarketPrice}
                        Property info to weight. Use one of yfinance info
                        options. (default: None)
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}
                        Risk measure used to optimize the portfolio (default:
                        MV)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00185)
  -a ALPHA, --alpha ALPHA
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  --hist                Display a histogram with risk measures (default:
                        False)
  --dd                  Display a drawdown chart with risk measures (default:
                        False)
  --rc-chart            Display a risk contribution chart for assets (default:
                        False)
  --heat                Display a heatmap of correlation matrix with
                        dendrogram (default: False)
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