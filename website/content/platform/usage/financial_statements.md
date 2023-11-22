---
title: Financial Statements
sidebar_position: 5
description: This page provides an introduction to financial statement data available in the OpenBB 
  Platform.  This includes quarterly and annual reports, along with metrics and ratios by company.
  This guide provides examples for using the variety of sources. 
keywords:
- stocks
- companies
- earnings
- dividends
- expectations
- dividend yield
- analyst consensus
- EPS
- assets
- total assets
- financial statements
- cash flow statement
- income statement
- balance sheet
- ratios
- quick ratio
- dividends
- market cap
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Financial Statements - Usage | OpenBB Platform Docs" />

OpenBB Platform data extensions provide access to financial statements as quarterly or annual.  There are also endpoints for ratios and other common non-GAAP metrics.  Most data providers require a subscription to access all data, refer to the website of a specific provider for details on entitlements and coverage.

Financial statement functions are grouped under the `obb.equity.fundamental` module.

## Financial Statements

The typical financial statements consist of three endpoints:

- Balance Sheet: `obb.equity.fundamental.balance()`
- Income Statement: `obb.equity.fundamental.income()`
- Cash Flow Statement: `obb.equity.fundamental.cash()`

The main parameters are:

- `symbol`: The company's ticker symbol.
- `period`: 'annual' or 'quarter'.  Default is 'annual'.
- `limit`: Limit the number of results returned, from the latest.  Default is 5.  For perspective, 150 will go back to 1985.  The amount of historical records varies by provider.

### Field Names

:::info

- Every data provider has their own way of parsing and organizing the three financial statements.
- Items within each statement will vary by source and by the type of company reporting.
- Names of line items will vary by source.
- "Date" values may differ because they are from the period starting/ending or date of reporting.
:::

This example highlights how different providers will have different labels for compnay facts.

```python
import pandas as pd

df = pd.DataFrame()

df["yfinance"] = (
  obb.equity.fundamental.balance("TGT", provider="yfinance", limit=4)
  .to_df()["TotalAssets"].reset_index(drop=True)
)
df["fmp"] = (
  obb.equity.fundamental.balance("TGT", provider="fmp", limit=4)
  .to_df()["assets"].convert_dtypes().reset_index(drop=True)
)
df["intrinio"] = (
  obb.equity.fundamental.balance("TGT", provider="intrinio", limit=4)
  .to_df()["total assets"].convert_dtypes().reset_index(drop=True)
)
df["polygon"] = (
  obb.equity.fundamental.balance("TGT", provider="polygon", limit=4)
  .to_df()["total_assets"].convert_dtypes().reset_index(drop=True)
)

df
```

|    |    yfinance |         fmp |    intrinio |     polygon |
|---:|------------:|------------:|------------:|------------:|
|  0 | 42779000000 | 42779000000 | 42779000000 | 42779000000 |
|  1 | 51248000000 | 51248000000 | 51248000000 | 51248000000 |
|  2 | 53811000000 | 53811000000 | 53811000000 | 53811000000 |
|  3 | 53335000000 | 53335000000 | 53335000000 | 53335000000 |

### Weighted Average Shares Outstanding

This key metric will be found under the income statement.  It might also be called, 'basic', and the numbers do not include authorized but unissued shares.  A declining count over time is a sign that the company is returning capital to shareholders in the form of buy backs.  Under ideal circumstances, it is more capital-efficient, for both company and shareholders, because distributions are double-taxed.  The company pays income tax on dividends paid, and the beneficiary pays income tax again on receipt.

A company will disclose how many shares are outstanding at the end of the period  as a weighted average over the reporting period - three months.

Let's take a look at Target.  To make the numbers easier to read, we'll divide the entire column by one million.

```python
data = (
  obb.equity.fundamental.income("TGT", provider='fmp', limit=150, period="quarter")
).to_df()
shares = data[["weighted_average_shares_outstanding"]]/1000000
```

Where this data starts,

```python
shares.head(1)
```

| date       |   weighted_average_shares_outstanding |
|:--------------------|--------------------------------------:|
| 1986-07-31 |                           1168.82 |

versus currently,

```python
shares.tail(1)
```

| date       |   weighted_average_shares_outstanding |
|:--------------------|--------------------------------------:|
| 2023-10-31 |                           461.6 |

Thirty-seven years later, the share count is approaching a two-thirds reduction.  12.2% over the past five years.

```python
shares.pct_change(20).iloc[-1].values[0]
```

```console
-0.12226659060657918
```

In four reporting periods, 1.3 million shares have been taken out of the float.

```python
shares.iloc[-4] - data.iloc[-1]
```

```console
weighted_average_shares_outstanding   -1.3
dtype: float64
```

With an average closing price of $143.37, that represents approximately $190M in buy backs.

```python
price = obb.equity.price.historical("TGT", start_date="2022-10-29", provider="fmp").to_df()

round((price["close"].mean()*1300000)/1000000, 2)
```

```console
186.38
```

### Dividends Paid

Dividends paid is in the cash flow statement.  We can calculate the amount-per-share with the reported data.

```python
dividends = (
  obb.equity.fundamental.cash("TGT", provider='fmp', limit=150, period="quarter").to_df()[["dividends_paid"]]
)
dividends["shares"] = data.to_df()[["weighted_average_shares_outstanding"]]
dividends["div_per_share"] = dividends["dividends_paid"]/dividends["shares"]

dividends["div_per_share"].tail(4)
```

| date          |   div_per_share |
|:--------------|----------------:|
| 2023-01-28  |        -1.07973 |
| 2023-04-29  |        -1.07833 |
| 2023-07-29  |        -1.08102 |
| 2023-10-31  |        -1.09835 |

This can be compared against the real amounts paid to common share holders with the historical dividend payments announced.

```python
obb.equity.fundamental.dividends("TGT", provider="fmp").to_df()["dividend"].tail(4)
```

| date          |   dividend |
|:--------------|-----------:|
| 2023-02-14  |       1.08 |
| 2023-05-16  |       1.08 |
| 2023-08-15  |       1.1  |
| 2023-11-14  |       1.1  |

The numbers check out, and the $2B paid to investors over four quarters is more than ten times the $190M returned through share buy backs.

### Financial Attributes

The `openbb-intrinio` data extension has an endpoint for extracting a single fact from financial statements.  There is a helper function for looking up the correct `tag`.

#### Seach Financial Attributes

Search attributes by keyword.

```python
obb.equity.fundamental.search_financial_attributes("marketcap")
```

|    | id         | name                  | tag       | statement_code   | statement_type   | parent_name   |   sequence | factor   | transaction   | type      | unit   |
|---:|:-----------|:----------------------|:----------|:-----------------|:-----------------|:--------------|-----------:|:---------|:--------------|:----------|:-------|
|  0 | tag_BgkbWy | Market Capitalization | marketcap | calculations     | industrial       |               |        nan |          |               | valuation | usd    |

The `tag` is what we need, in this case it is what we searched for.

```python
marketcap = obb.equity.fundamental.financial_attributes(symbol="TGT", tag = "marketcap", period="quarter").to_df()

marketcap.tail(4)
```

| date          |       value |
|:--------------|------------:|
| 2023-03-31  | 75023699391 |
| 2023-06-30  | 59916953938 |
| 2023-09-30  | 50614370690 |
| 2023-11-21  | 59963125000 |

Doing some quick math, we can see that the market cap of Target is down 20% over four reporting periods.

```python
(marketcap.iloc[-1] - marketcap.iloc[-4])/marketcap.iloc[-4].value
```

```console
-0.200744
```

## Ratios and Other Metrics

Other valuation functions are derivatives of the financial statements, but the data provider does the math.  Values are typically ratios between line items, on a per-share basis, or as a percent growth.

This data set is where you can find EPS, FCF, P/B, EBIT, quick ratio, etc.

Target's quick ratio could be one reason why its share price is losing traction against the market.  Its ability to pay current obligations is not optimistically reflected in a 0.27 score.

```python
ratios = obb.equity.fundamental.ratios("TGT", limit=50, provider="fmp").to_df()

ratios["quick_ratio"].iloc[-1]
```

```console
0.2701025641025641
```

This number falls about 50% below the historical median.

```python
ratios["quick_ratio"].median()
```

```console
0.5843795019551348
```

Explore the rest of the `fundamental` module under the [Reference](/platform/reference/equity/fundamental) section.
