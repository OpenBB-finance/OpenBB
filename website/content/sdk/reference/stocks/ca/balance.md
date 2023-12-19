---
title: balance
description: This page provides a detailed view on the balance data obtained through
  OpenBB Terminal's stocks comparison analysis. Python source code, parameters
  for the function and return type are conventionally presented.
keywords:
- balance data
- stocks comparison analysis
- marketwatch model
- tickers comparison
- quarterly statements
- data export
- dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ca.balance - Reference | OpenBB SDK Docs" />

Get balance data. [Source: Marketwatch].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/comparison_analysis/marketwatch_model.py#L107)]

```python
openbb.stocks.ca.balance(similar: List[str], timeframe: str = "2021", quarter: bool = False)
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
| pd.DataFrame | Dataframe of balance comparisons |
---
