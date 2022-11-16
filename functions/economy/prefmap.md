---
title: prefmap
description: OpenBB SDK Function
---

# prefmap

## economy_finviz_model.get_performance_map

```python title='openbb_terminal/economy/finviz_model.py'
def get_performance_map(period: str, map_filter: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L41)

Description: Opens Finviz map website in a browser. [Source: Finviz]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| period | str | Performance period. Available periods are 1d, 1w, 1m, 3m, 6m, 1y. | None | False |
| scope | str | Map filter. Available map filters are sp500, world, full, etf. | None | False |

## Returns

This function does not return anything

## Examples

