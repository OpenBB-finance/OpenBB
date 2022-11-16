---
title: kelly
description: OpenBB SDK Function
---

# kelly

## portfolio_model.get_kelly_criterion

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_kelly_criterion(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1286)

Description: Gets kelly criterion

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of kelly criterion of the portfolio during different time periods |

## Examples

