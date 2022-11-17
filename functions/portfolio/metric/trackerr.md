---
title: trackerr
description: OpenBB SDK Function
---

# trackerr

## portfolio_model.get_tracking_error

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_tracking_error(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1122)

Description: Get tracking error

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | int | Interval used for rolling values | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of tracking errors during different time windows |

## Examples

