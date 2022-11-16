---
title: kurtosis
description: OpenBB SDK Function
---

# kurtosis

## portfolio_model.get_kurtosis

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_kurtosis(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L862)

Description: Class method that retrieves kurtosis for portfolio and benchmark selected

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with kurtosis for portfolio and benchmark for different periods |

## Examples

