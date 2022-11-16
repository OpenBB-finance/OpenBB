---
title: om
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# om

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_model.get_omega

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_omega(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, threshold_start: float, threshold_end: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1757)

Description: Get omega ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | None | False |
| threshold_end | float | annualized target return threshold end of plotted threshold range | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_view.display_omega

```python title='openbb_terminal/portfolio/portfolio_view.py'
def display_omega(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, threshold_start: float, threshold_end: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L1686)

Description: Display omega ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | None | False |
| threshold_end | float | annualized target return threshold end of plotted threshold range | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>