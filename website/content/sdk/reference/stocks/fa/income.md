---
title: income
description: This page is a detailed guide on how to use the 'income' function provided
  by OpenBBTerminal. This function fetches income statements for a given stock symbol
  from selected data sources like YahooFinance or AlphaVantage.
keywords:
- income statement
- stock
- symbol
- source
- YahooFinance
- AlphaVantage
- OpenBBTerminal income
- Financial Analysis
- fundamental analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.income - Reference | OpenBB SDK Docs" />

Get income statement.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py#L14)]

```python
openbb.stocks.fa.income(symbol: str, quarterly: bool = False, ratios: bool = False, source: str = "YahooFinance", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get income statement for | None | False |
| source | str | Data source for income statement, by default "YahooFinance" | YahooFinance | True |
| quarterly | bool | Flag to get quarterly data | False | True |
| ratios | bool | Flag to return data as a percent change. | False | True |
| limit | int | Number of statements to return (free tiers may be limited to 5 years) | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of income statement |
---

## Examples

```python
from openbb_terminal.sdk import openbb
income_statement = openbb.stocks.fa.income("AAPL", source="YahooFinance)
```

```
If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
```
```python
quarterly_income_statement = openbb.stocks.fa.income("AAPL", source="AlphaVantage", quarterly=True)
```

---
