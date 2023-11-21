---
title: balance
description: This page provides detailed information for retrieving balance sheet
  data via the OpenBBTerminal's Python function. This includes the parameters and
  return type of the function, as well as examples of its use for different data sources
  specifically for the stock symbol 'AAPL'.
keywords:
- balance sheet
- financial data
- YahooFinance
- AlphaVantage
- stock symbol
- AAPL
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.balance - Reference | OpenBB SDK Docs" />

Get balance sheet.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py#L77)]

```python
openbb.stocks.fa.balance(symbol: str, quarterly: bool = False, ratios: bool = False, source: str = "YahooFinance", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get balance sheet for | None | False |
| source | str | Data source for balance sheet, by default "YahooFinance" | YahooFinance | True |
| quarterly | bool | Flag to get quarterly data | False | True |
| ratios | bool | Flag to return data as a percent change. | False | True |
| limit | int | Number of statements to return (free tiers may be limited to 5 years) | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of balance sheet |
---

## Examples

```python
from openbb_terminal.sdk import openbb
balance_sheet = openbb.stocks.fa.balance("AAPL", source="YahooFinance)
```

```
If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
```
```python
quarterly_income_statement = openbb.stocks.fa.balance("AAPL", source="AlphaVantage", quarterly=True)
```

---
