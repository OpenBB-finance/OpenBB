---
title: lobbying
description: This page provides details on corporate lobbying, including parameters
  for symbol and limit, and returns a dataframe with corporate lobbying data. It includes
  a link to the source code on GitHub.
keywords:
- Corporate lobbying details
- Source code
- openbb.stocks.gov.lobbying
- Parameters
- symbol
- Ticker symbol
- limit
- Returns
- corporate lobbying data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.gov.lobbying - Reference | OpenBB SDK Docs" />

Corporate lobbying details

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L531)]

```python
openbb.stocks.gov.lobbying(symbol: str, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get corporate lobbying data from | None | False |
| limit | int | Number of events to show | 10 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with corporate lobbying data |
---
