---
title: process_candle
description: OpenBB SDK Function
---

# process_candle

## stocks_helper.process_candle

```python title='openbb_terminal/stocks/stocks_helper.py'
def process_candle(data: pd.DataFrame) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L800)

Description: Process DataFrame into candle style plot.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | DataFrame | Stock dataframe. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume,
date_id, OC-High, OC-Low. |

## Examples

