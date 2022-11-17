---
title: jensens
description: OpenBB SDK Function
---

# jensens

## portfolio_model.get_jensens_alpha

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_jensens_alpha(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, risk_free_rate: float, window: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1223)

Description: Get jensen's alpha

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | str | Interval used for rolling values | None | False |
| risk_free_rate | float | Risk free rate | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of jensens's alpha during different time windows |

## Examples

