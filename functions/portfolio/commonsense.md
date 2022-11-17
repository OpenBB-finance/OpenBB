---
title: commonsense
description: OpenBB SDK Function
---

# commonsense

## portfolio_model.get_common_sense_ratio

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_common_sense_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1199)

Description: Get common sense ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of the portfolios and the benchmarks common sense ratio during different time periods |

## Examples

