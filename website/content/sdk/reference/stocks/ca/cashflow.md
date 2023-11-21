---
title: cashflow
description: This page discusses the cashflow data from Marketwatch. It explains how
  to use the openbb.stocks.ca.cashflow function, its parameters, and outputs, emphasizing
  on a dataframe of cashflow comparisons.
keywords:
- cashflow data
- marketwatch source code
- openbb.stocks.ca.cashflow function
- parameters
- dataframe of cashflow comparisons
- timeframe
- quarter
- export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.cashflow - Reference | OpenBB SDK Docs" />

Get cashflow data. [Source: Marketwatch]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/marketwatch_model.py#L140)]

```python
openbb.stocks.ca.cashflow(similar: List[str], timeframe: str = "2021", quarter: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| similar | List[str] | List of tickers to compare.<br/>Comparable companies can be accessed through<br/>finnhub_peers(), finviz_peers(), polygon_peers(). | None | False |
| timeframe | str | Column header to compare | 2021 | True |
| quarter | bool | Whether to use quarterly statements, by default False | False | True |
| export | str | Format to export data | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of cashflow comparisons |
---
