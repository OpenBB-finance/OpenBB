---
title: supplier
description: OpenBB SDK Function
---

# supplier

## stocks_dd_csimarket_model.get_suppliers

```python title='openbb_terminal/stocks/due_diligence/csimarket_model.py'
def get_suppliers(symbol: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/csimarket_model.py#L42)

Description: Get suppliers from ticker provided. [Source: CSIMarket]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to select suppliers from | None | False |
| limit | int | The maximum number of rows to show | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A dataframe of suppliers |

## Examples

