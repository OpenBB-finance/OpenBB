---
title: cash
description: Improve financial analysis with OpenBB's Cash Flow feature. Retrieve
  historical cash flow data for any stock symbol using various sources like YahooFinance
  with options to get quarterly data and data as a percentage change.
keywords:
- Cash Flow
- Financial Analysis
- Stock Symbol
- YahooFinance
- AlphaVantage
- ' quarterly data'
- percentage change
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.cash - Reference | OpenBB SDK Docs" />

Get Cash Flow.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py#L140)]

```python
openbb.stocks.fa.cash(symbol: str, quarterly: bool = False, ratios: bool = False, source: str = "YahooFinance", limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get cash flow for | None | False |
| source | str | Data source for cash flow, by default "YahooFinance" | YahooFinance | True |
| quarterly | bool | Flag to get quarterly data | False | True |
| ratios | bool | Flag to return data as a percent change. | False | True |
| limit | int | Number of statements to return (free tiers may be limited to 5 years) | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of cash flow |
---

## Examples

```python
from openbb_terminal.sdk import openbb
cash_flow = openbb.stocks.fa.cash("AAPL", source="YahooFinance)
```

```
If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
```
```python
quarterly_income_statement = openbb.stocks.fa.cash("AAPL", source="AlphaVantage", quarterly=True)
```

---
