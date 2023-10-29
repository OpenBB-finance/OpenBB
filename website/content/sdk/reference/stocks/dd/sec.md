---
title: sec
description: This page provides the source code and related information for using
  OpenBB's SEC filings feature. Retrieve stock ticker information from platforms like
  Market Watch. Written in Python, the feature returns SEC filings data in a pd.DataFrame
  format.
keywords:
- SEC filings
- stock ticker
- Market Watch
- stocks
- due diligence
- marketwatch model
- symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dd.sec - Reference | OpenBB SDK Docs" />

Get SEC filings for a given stock ticker. [Source: Market Watch]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/marketwatch_model.py#L20)]

```python
openbb.stocks.dd.sec(symbol: str)
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
| pd.DataFrame | SEC filings data |
---
