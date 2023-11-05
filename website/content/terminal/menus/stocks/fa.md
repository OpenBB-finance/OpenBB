---
title: Fundamental Analysis
description: The Fundamental Analysis menu is a set of tools for analyzing the overall health of a company and estimating its intrinsic value. Functions within this menu provide company profiles, financial statements, historical distributions, financial ratios, and analyst estimates.
keywords:
- fundamental analysis
- financials
- consensus
- estimates
- price target
- SEC filings
- shareholder
- ratios
- fundamentals
- management
- ratings
- eps
- dcf
- customers
- suppliers
- distributions
- analyst
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Fundamental Analysis - Stocks - Menus | OpenBB Terminal Docs" />

The Fundamental Analysis menu is a set of tools for analyzing the overall health of a company and estimating its intrinsic value.  Functions within this menu provide company profiles, financial statements, historical distributions, financial ratios, and analyst estimates.  Revenue of companies with a long public history are easier to forecast, and the consensus of many analysts will indicate the level of confidence in future expectations. In addition to these features, there are tools in the [`stocks/ca`](/terminal/menus/stocks/comparison.md) menu for comparing fundamentals across groups of companies.

## Usage

Enter the submenu from the `/stocks/` menu with `fa`, or from the absolute path:

```console
/stocks/fa
```

![Screenshot 2023-11-01 at 10 03 40 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/21a947f2-b173-493f-a1e4-b889deef32c4)

:::note

- All functions in this menu can add a ticker argument with the `-t` flag.  This overrides the loaded symbol.

- Data returned from each source will be different for the same command.  Use the `--source` argument to change the data provider for a command with more than one available.

:::

### Overview

The `overview` command provides general metadata and key metrics.

```console
/stocks/fa/overview -t aapl --source YahooFinance
```

|                               | Value              |
|:------------------------------|:-------------------|
| Currency                      | USD                |
| Day high                      | 172.36000061035156 |
| Day low                       | 170.1300048828125  |
| Exchange                      | NMS                |
| Fifty day average             | 176.71860076904298 |
| Last price                    | 172.35000610351562 |
| Last volume                   | 23223500           |
| Market cap                    | 2694554388210.7812 |
| Open                          | 171.0              |
| Previous close                | 170.38             |
| Quote type                    | EQUITY             |
| Regular market previous close | 170.77000427246094 |
| Shares                        | 15634199552        |
| Ten day average volume        | 56025390           |
| Three month average volume    | 58964427           |
| Timezone                      | America/New_York   |
| Two hundred day average       | 170.8950003814697  |
| Year change                   | 0.177480560641351  |
| Year high                     | 198.22999572753906 |
| Year low                      | 124.16999816894531 |


An example of the difference between sources:

```console
/stocks/fa/overview -t aapl --source AlphaVantage
```

|                            |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|:---------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Symbol                     | AAPL                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| AssetType                  | Common Stock                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Name                       | Apple Inc                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Description                | Apple Inc. is an American multinational technology company that specializes in consumer electronics, computer software, and online services. Apple is the world's largest technology company by revenue (totalling $274.5 billion in 2020) and, since January 2021, the world's most valuable company. As of 2021, Apple is the world's fourth-largest PC vendor by unit sales, and fourth-largest smartphone manufacturer. It is one of the Big Five American information technology companies, along with Amazon, Google, Microsoft, and Facebook. |
| CIK                        | 320193                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Exchange                   | NASDAQ                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| Currency                   | USD                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Country                    | USA                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Sector                     | TECHNOLOGY                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Industry                   | ELECTRONIC COMPUTERS                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Address                    | ONE INFINITE LOOP, CUPERTINO, CA, US                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| FiscalYearEnd              | September                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| LatestQuarter              | 2023-06-30                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| MarketCapitalization       | 2669852230000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| EBITDA                     | 123957002000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| PERatio                    | 28.65                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| PEGRatio                   | 2.75                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| BookValue                  | 3.852                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| DividendPerShare           | 0.93                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| DividendYield              | 0.0056                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| EPS                        | 5.96                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| RevenuePerShareTTM         | 24.22                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ProfitMargin               | 0.247                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| OperatingMarginTTM         | 0.281                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ReturnOnAssetsTTM          | 0.209                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ReturnOnEquityTTM          | 1.601                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| RevenueTTM                 | 383932989000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| GrossProfitTTM             | 170782000000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| DilutedEPSTTM              | 5.96                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| QuarterlyEarningsGrowthYOY | 0.05                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| QuarterlyRevenueGrowthYOY  | -0.014                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| AnalystTargetPrice         | 187.73                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| TrailingPE                 | 28.65                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ForwardPE                  | 28.66                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| PriceToSalesRatioTTM       | 5.51                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| PriceToBookRatio           | 44.63                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| EVToRevenue                | 5.92                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| EVToEBITDA                 | 23.52                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Beta                       | 1.308                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 52WeekHigh                 | 197.96                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 52WeekLow                  | 123.64                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 50DayMovingAverage         | 176.72                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 200DayMovingAverage        | 170.9                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| SharesOutstanding          | 15634200000                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| DividendDate               | 2023-08-17                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ExDividendDate             | 2023-08-11                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |


### Analysis

The `analysis` command reads SEC filings with NLP and extracts the most important statements.  Source: [https://eclect.us/](https://eclect.us/)

![Screenshot 2023-11-01 at 10 20 44 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/771f1f60-7879-4243-bbb5-2d2298ea4ecf)

### MKTCAP

The `mktcap` command will display the historical market cap of the company.  When the `--source` is `FinancialModelingPrep`, the enterprise value can be chosen as the target metric.

```console
/stocks/fa/mktcap -t aapl --source FinancialModelingPrep ---method enterprise_value --quarter
```

![Screenshot 2023-11-01 at 10 29 30 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/41fb942b-dffc-4ab9-b6b8-62884b9faf8d)

### Earnings

The `earnings` command compares reported EPS to estimated for each period.

```console
/stocks/fa/earnings -t aapl --quarter
```

![Screenshot 2023-11-01 at 10 59 35 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/fa03681a-11ff-4a33-8832-fa47246ed44c)

### EPSFC

`epsfc` is the forward consensus of EPS estimates.

```console
/stocks/fa/epsfc -t aapl
```

|   fiscalyear |   consensus_mean |   change % |   analysts |   actual |   consensus_low |   consensus_high |
|-------------:|-----------------:|-----------:|-----------:|---------:|----------------:|-----------------:|
|         2022 |          6.10809 |   8.87861  |         41 |     6.11 |            5.96 |             6.4  |
|         2023 |          6.07227 |  -0.617512 |         43 |     0    |            5.82 |             6.53 |
|         2024 |          6.53322 |   7.59107  |         43 |     0    |            5.6  |             7.1  |
|         2025 |          7.11054 |   8.83668  |         19 |     0    |            6.09 |             7.98 |
|         2026 |          8.12    |  14.1967   |          2 |     0    |            7.18 |             9.06 |
|         2027 |          9.08    |  11.8227   |          2 |     0    |            8.03 |            10.13 |
|         2028 |          8.96    |  -1.32159  |          1 |     0    |            8.96 |             8.96 |
|         2029 |          9.96    |  11.1607   |          1 |     0    |            9.96 |             9.96 |
|         2030 |         10.99    |  10.3414   |          1 |     0    |           10.99 |            10.99 |
|         2031 |         12.14    |  10.4641   |          1 |     0    |           12.14 |            12.14 |
|         2032 |         13.44    |  10.7084   |          1 |     0    |           13.44 |            13.44 |

### Ratios

The `ratios` command returns calculated financial ratios, by year or quarter.  To get quarterly data, apply the `--quarter` flag.  Use the `--limit` argument to return more results.

```console
/stocks/fa/ratios -t aapl
```

![Screenshot 2023-11-01 at 10 54 48 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/2eb8dd17-1dd3-4d85-9f70-318037015285)


### DCF

The `dcf` function will attempt to generate a discounted cash flow statement as an Excel file.  See the optional arguments that can be applied to the command by adding `-h` to the syntax.

```console
/stocks/fa/dcf -h
```

The available parameters are:

```console
  -t TICKER, --ticker TICKER
                        Ticker to analyze (default: None)
  -a, --audit           Generates a tie-out for financial statement information pulled from online. (default: False)
  --no-ratios           Removes ratios from DCF. (default: True)
  --no-filter           Allow similar companies of any market cap to be shown. (default: False)
  -p PREDICTION, --prediction PREDICTION
                        Number of years to predict before using terminal value. (default: 10)
  -s SIMILAR, --similar SIMILAR
                        Number of similar companies to generate ratios for. (default: 0)
  -b BETA, --beta BETA  The beta you'd like to use for the calculation. (default: 1)
  -g, --growth          Whether to replace a linear regression estimate with a growth estimate. (default: False)
  -h, --help            show this help message (default: False)
```

![Screenshot 2023-11-01 at 11 15 06 AM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/6bc9861a-9dc1-4425-8f09-5f29d5619f9d)
