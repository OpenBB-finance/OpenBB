---
title: est
description: OpenBB SDK Function
---

# est

## stocks_dd_business_insider_model.get_estimates

```python title='openbb_terminal/stocks/due_diligence/business_insider_model.py'
def get_estimates(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/due_diligence/business_insider_model.py#L71)

Description: Get analysts' estimates for a given ticker. [Source: Business Insider]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get analysts' estimates | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Year estimates |

## Examples

