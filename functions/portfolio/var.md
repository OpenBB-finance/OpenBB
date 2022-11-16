---
title: var
description: OpenBB SDK Function
---

# var

## portfolio_model.get_var

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_var(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, use_mean: bool, adjusted_var: bool, student_t: bool, percentile: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1685)

Description: Get portfolio VaR

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| use_mean | bool | if one should use the data mean return | None | False |
| adjusted_var | bool | if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion) | None | False |
| student_t | bool | If one should use the student-t distribution | None | False |
| percentile | float | var percentile (%) | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples

