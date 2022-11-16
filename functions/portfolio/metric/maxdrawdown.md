---
title: maxdrawdown
description: OpenBB SDK Function
---

# maxdrawdown

## portfolio_model.get_maximum_drawdown_ratio

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_maximum_drawdown_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1060)

Description: Class method that retrieves maximum drawdown ratio for portfolio and benchmark selected

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with maximum drawdown for portfolio and benchmark for different periods |

## Examples

