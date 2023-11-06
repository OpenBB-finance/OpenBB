---
title: messages
description: This page provides information regarding the 'get last messages for a
  given ticker' function in the OpenBB Terminal. It explains the usage and parameters
  of the function.
keywords:
- stock messages
- stock ticker
- Stocktwits messages
- data analysis
- behavioural analysis on stocks
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.ba.messages - Reference | OpenBB SDK Docs" />

Get last messages for a given ticker [Source: stocktwits].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/stocktwits_model.py#L52)]

```python
openbb.stocks.ba.messages(symbol: str, limit: int = 30)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of messages to get | 30 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of messages |
---
