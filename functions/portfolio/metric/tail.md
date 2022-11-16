---
title: tail
description: OpenBB SDK Function
---

# tail

## portfolio_model.get_tail_ratio

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_tail_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1171)

Description: Get tail ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | int | Interval used for rolling values | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of the portfolios and the benchmarks tail ratio during different time windows |

## Examples

