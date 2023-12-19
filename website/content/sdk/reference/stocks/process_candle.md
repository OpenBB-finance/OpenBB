---
title: process_candle
description: Learn how to use OpenBB's process_candle function to manipulate stock
  data into a candle style plot. Particularly useful tool for financial analysis.
keywords:
- OpenBB stocks
- process_candle
- Stock DataFrame
- Panda's DataFrame
- Stock market
- Finance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.process_candle - Reference | OpenBB SDK Docs" />

Process DataFrame into candle style plot.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L825)]

```python
openbb.stocks.process_candle(data: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | DataFrame | Stock dataframe. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,<br/>date_id, OC-High, OC-Low. |
---
