---
title: cal
description: This page provides a python function for fetching calendar earnings of
  a specific stock ticker symbol using the OpenBB Terminal library. The function returns
  a pandas dataframe with the earnings data.
keywords:
- calendar earnings
- ticker symbol
- openbb.stocks.fa.cal()
- stock fundamental analysis
- Python finance library
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.fa.cal - Reference | OpenBB SDK Docs" />

Get calendar earnings for ticker symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L179)]

```python
openbb.stocks.fa.cal(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of calendar earnings |
---
