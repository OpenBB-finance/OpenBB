---
title: mret
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mret

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_model.get_monthly_returns

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_monthly_returns(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1900)

Description: Get monthly returns

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | str | interval to compare cumulative returns and benchmark | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_view.display_monthly_returns

```python title='openbb_terminal/portfolio/portfolio_view.py'
def display_monthly_returns(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str, raw: bool, show_vals: bool, export: str, external_axes: Optional[matplotlib.axes._axes.Axes]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L369)

Description: Display monthly returns

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | str | interval to compare cumulative returns and benchmark | None | False |
| raw | False | Display raw data from cumulative return | None | False |
| show_vals | False | Show values on heatmap | None | False |
| export | str | Export certain type of data | None | False |
| external_axes | plt.Axes | Optional axes to display plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>