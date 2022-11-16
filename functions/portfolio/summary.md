---
title: summary
description: OpenBB SDK Function
---

# summary

## portfolio_model.get_summary

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_summary(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str, risk_free_rate: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1783)

Description: Get summary portfolio and benchmark returns

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | str | interval to compare cumulative returns and benchmark | None | False |
| risk_free_rate | float | Risk free rate for calculations | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples

