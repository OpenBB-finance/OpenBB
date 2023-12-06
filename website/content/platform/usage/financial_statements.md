---
title: Financial Statements
sidebar_position: 6
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

OpenBB Platform data extensions provide access to financial statements as quarterly or annual. There are also endpoints for ratios and other common non-GAAP metrics. Most data providers require a subscription to access all data, refer to the website of a specific provider for details on entitlements and coverage.

Financial statement functions are grouped under the `obb.equity.fundamental` module.

:::info
To begin, import the OpenBB Platform into a Python session:

```python
from openbb import obb
```

:::

## Financial Statements

The typical financial statements consist of three endpoints:

- Balance Sheet: `obb.equity.fundamental.balance()`
- Income Statement: `obb.equity.fundamental.income()`
- Cash Flow Statement: `obb.equity.fundamental.cash()`

The main parameters are:

- `symbol`: The company's ticker symbol.
- `period`: 'annual' or 'quarter'. Default is 'annual'.
- `limit`: Limit the number of results returned, from the latest. Default is 5. For perspective, 150 will go back to 1985. The amount of historical records varies by provider.

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

This key metric will be found under the income statement. It might also be called, 'basic', and the numbers do not include authorized but unissued shares. A declining count over time is a sign that the company is returning capital to shareholders in the form of buy backs. Under ideal circumstances, it is more capital-efficient, for both company and shareholders, because distributions are double-taxed. The company pays income tax on dividends paid, and the beneficiary pays income tax again on receipt.

A company will disclose how many shares are outstanding at the end of the period  as a weighted average over the reporting period - three months.

Let's take a look at Target.  To make the numbers easier to read, we'll divide the entire column by one million.

```python
data = (
  obb.equity.fundamental.income("TGT", provider='fmp', limit=150, period="quarter")
  .to_df()
)

shares = data["weighted_average_shares_outstanding"]/1000000
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
shares.pct_change(20).iloc[-1]
```

```console
-0.12
```

In four reporting periods, 1.3 million shares have been taken out of the float.

```python
shares.iloc[-4] - shares.iloc[-1]
```

```console
-1.3
```

With an average closing price of $144.27, that represents approximately $190M in buy backs.

```python
price = (
  obb.equity.price.historical("TGT", start_date="2022-10-01", provider="fmp")
  .to_df()
)

round((price["close"].mean()*1300000)/1000000, 2)
```

```console
187.55
```

### Dividends Paid

Dividends paid is in the cash flow statement. We can calculate the amount-per-share with the reported data.

```python
dividends = (
  obb.equity.fundamental.cash("TGT", provider='fmp', limit=150, period="quarter")
  .to_df()[["dividends_paid"]]
)

dividends["shares"] = data[["weighted_average_shares_outstanding"]]
dividends["div_per_share"] = dividends["dividends_paid"]/dividends["shares"]

dividends["div_per_share"].tail(4)
```

| date          |   div_per_share |
|:--------------|----------------:|
| 2023-01-28  |        -1.07973 |
| 2023-04-29  |        -1.07833 |
| 2023-07-29  |        -1.08102 |
| 2023-10-31  |        -1.09835 |

This can be compared against the real amounts paid to common share holders, as announced.

:::note
The dates immediately above represent the report date, dividends paid are attributed to the quarter they were paid in. The value from "2023-01-28" equates to the fourth quarter of 2022.
:::

```python
(
  obb.equity.fundamental.dividends("TGT", provider="fmp")
  .to_df()["dividend"]
  .loc["2022-11-15":"2023-08-15"]
)
```

 date          |   dividend |
|:--------------|-----------:|
| 2022-11-15  |       1.08 |
| 2023-02-14  |       1.08 |
| 2023-05-16  |       1.08 |
| 2023-08-15  |       1.1  |

The numbers check out, and the $2B paid to investors over four quarters is more than ten times the $190M returned through share buy backs.

### Financial Attributes

The `openbb-intrinio` data extension has an endpoint for extracting a single fact from financial statements. There is a helper function for looking up the correct `tag`.

#### Search Financial Attributes

Search attributes by keyword.

```python
obb.equity.fundamental.search_attributes("marketcap").head(1)
```

|    | id         | name                  | tag       | statement_code   | statement_type   | parent_name   |   sequence | factor   | transaction   | type      | unit   |
|---:|:-----------|:----------------------|:----------|:-----------------|:-----------------|:--------------|-----------:|:---------|:--------------|:----------|:-------|
|  0 | tag_BgkbWy | Market Capitalization | marketcap | calculations     | industrial       |               |        nan |          |               | valuation | usd    |

The `tag` is what we need, in this case it is what we searched for.

```python
marketcap = (
  obb.equity.fundamental.historical_attributes(symbol="TGT", tag = "marketcap", frequency="quarterly")
  .to_df()
)

marketcap.tail(5)
```

| date          |       value |
|:--------------|------------:|
| 2022-12-31  | 66929627287 |
| 2023-03-31  | 75023699391 |
| 2023-06-30  | 59916953938 |
| 2023-09-30  | 50614370690 |
| 2023-11-22  |  60495000000 |

Doing some quick math, and ignoring the most recent value, we can see that the market cap of Target was down nearly a quarter over the last four reporting periods.

```python
(
    (marketcap.loc["2023-09-30"] - marketcap.loc["2022-12-31"])/marketcap.loc["2022-12-31"]
).value
```

```console
-0.24
```

## Ratios and Other Metrics

Other valuation functions are derivatives of the financial statements, but the data provider does the math. Values are typically ratios between line items, on a per-share basis, or as a percent growth.

This data set is where you can find EPS, FCF, P/B, EBIT, quick ratio, etc.

### Quick Ratio

Target's quick ratio could be one reason why its share price is losing traction against the market. Its ability to pay current obligations is not optimistically reflected in a 0.27 score, approximately 50% below the historical median.

```python
ratios = (
  obb.equity.fundamental.ratios("TGT", limit=50, provider="fmp")
  .to_df()
)

display(f"Current Quick Ratio: {ratios['quick_ratio'].iloc[-1]}")
display(f"Median Quick Ratio: {ratios['quick_ratio'].median()}")
```

```console
Current Quick Ratio: 0.27
Median Quick Ratio: 0.58
```

### Free Cash Flow Yield

The `metrics` endpoint, with the `openbb-fmp` data extension, has a field for free cash flow yield. It is calculated by taking the free cash flow per share divided by the current share price. We could arrive at this answer by writing some code, but these types of endpoints do the work so we don't have to. This is part of the value-add that API data distributors provide, they allow you to get straight to work with data.

We'll use this endpoint to extract the data, and compare with some of Target's competition over the last ten years.

```python
# List of other retail chains
tickers = ["COST", "BJ", "DLTR", "DG", "WMT", "BIG", "M", "KSS", "TJX"]
# Create a dictionary of tickers and company names.
names = {
    ticker: obb.equity.fundamental.overview(ticker, provider="fmp").results.company_name
    for ticker in tickers
}
# Create a column for each.
fcf_yield = pd.DataFrame()
for ticker in tickers:
    fcf_yield[names[ticker]] = (
        obb.equity.fundamental.metrics(ticker, provider="fmp", period="annual", limit=10)
        .to_df()
        .reset_index()
        .set_index("calendar_year")
        .sort_index(ascending=False)
        ["free_cash_flow_yield"]
    )
fcf_yield.transpose()
```

|                                    |        2023 |        2022 |      2021 |      2020 |      2019 |       2018 |      2017 |       2016 |      2015 |        2014 |
|:-----------------------------------|------------:|------------:|----------:|----------:|----------:|-----------:|----------:|-----------:|----------:|------------:|
| Costco Wholesale Corporation       |   0.0279218 |  0.0148596  | 0.0265818 | 0.0393512 | 0.0259061 |  0.0274379 | 0.0608836 | 0.00894059 | 0.0307414 |   0.0374833 |
| BJ's Wholesale Club Holdings, Inc. | nan         |  0.0447092  | 0.0672128 | 0.113551  | 0.0566305 |  0.0911069 | 0.0261863 | 0.0658713  | 0.0169474 | nan         |
| Dollar Tree, Inc.                  | nan         |  0.010756   | 0.013957  | 0.075627  | 0.040338  |  0.0412519 | 0.0340694 | 0.0634655  | 0.0166025 |   0.0410471 |
| Dollar General Corporation         | nan         |  0.00825589 | 0.0375074 | 0.0589731 | 0.0369217 |  0.0461971 | 0.0426088 | 0.0507761  | 0.0395241 |   0.0460518 |
| Walmart Inc.                       |   0.0312425 |  0.028372   | 0.0654622 | 0.0445913 | 0.062023  |  0.0572749 | 0.101038  | 0.0735059  | 0.0597117 |   0.0415436 |
| Big Lots, Inc.                     | nan         | -0.550469   | 0.0252616 | 0.115757  | 0.0694642 | -0.111853  | 0.037219  | 0.100721   | 0.110443  |   0.089253  |
| Macy's, Inc.                       | nan         |  0.0504726  | 0.27098   | 0.0391114 | 0.0913008 |  0.101426  | 0.155761  | 0.098993   | 0.0656336 |   0.072322  |
| Kohl's Corporation                 | nan         | -0.143961   | 0.189677  | 0.147968  | 0.119492  |  0.139799  | 0.0961367 | 0.19879    | 0.0816518 |   0.110697  |
| The TJX Companies, Inc.            |   0.0271588 |  0.0234975  | 0.0517687 | 0.0401668 | 0.0488266 |  0.0399352 | 0.0536965 | 0.0433279  | 0.0464416 |   0.0406432 |

Explore the rest of the `fundamental` module under the [Reference](/platform/reference/equity/fundamental) section.
