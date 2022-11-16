---
title: volatility
description: OpenBB SDK Function
---

# volatility

## portfolio_model.get_volatility

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_volatility(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L931)

Description: Class method that retrieves volatility for portfolio and benchmark selected

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with volatility for portfolio and benchmark for different periods |

## Examples

