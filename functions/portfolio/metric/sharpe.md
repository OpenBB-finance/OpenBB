---
title: sharpe
description: OpenBB SDK Function
---

# sharpe

## portfolio_model.get_sharpe_ratio

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_sharpe_ratio(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, risk_free_rate: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L970)

Description: Class method that retrieves sharpe ratio for portfolio and benchmark selected

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| risk_free_rate | float | Risk free rate value | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with sharpe ratio for portfolio and benchmark for different periods |

## Examples

