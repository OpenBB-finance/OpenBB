---
title: calmar
description: OpenBB SDK Function
---

# calmar

## portfolio_model.get_calmar_ratio

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_calmar_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1257)

Description: Get calmar ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | int | Interval used for rolling values | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of calmar ratio of the benchmark and portfolio during different time periods |

## Examples

