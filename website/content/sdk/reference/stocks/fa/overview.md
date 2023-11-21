---
title: overview
description: This page provides an API for getting an Alpha Vantage's company overview
  with OpenBB Terminal. It is implemented with Python for stock fundamental analysis.
  A stock's ticker symbol is used as the parameter, and it returns the fundamentals
  in a pd.DataFrame.
keywords:
- Alpha vantage company overview
- OpenBB finance
- OpenBB terminal
- Stocks fundamental analysis
- AV model
- Stock ticker symbol
- Dataframe of fundamentals
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.overview - Reference | OpenBB SDK Docs" />

Get overview.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py#L17)]

```python wordwrap
openbb.stocks.fa.overview(symbol: str, source: str = "YahooFinance")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get overview for | None | False |
| source | str | Data source for overview, by default "YahooFinance"<br/>Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Finviz | YahooFinance | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of overview |
---

## Examples

```python
from openbb_terminal.sdk import openbb
overview = openbb.stocks.fa.overview("AAPL", source="AlphaVantage")
```

---

