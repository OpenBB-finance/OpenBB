---
title: lobbying
description: OpenBB SDK Function
---

# lobbying

## stocks_gov_quiverquant_model.get_lobbying

```python title='openbb_terminal/stocks/government/quiverquant_model.py'
def get_lobbying(symbol: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L531)

Description: Corporate lobbying details

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get corporate lobbying data from | None | False |
| limit | int | Number of events to show | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with corporate lobbying data |

## Examples

