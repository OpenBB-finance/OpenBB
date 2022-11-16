---
title: distr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# distr

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_model.get_distribution_returns

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_distribution_returns(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1415)

Description: Display daily returns

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| window | str | interval to compare cumulative returns and benchmark | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_view.display_distribution_returns

```python title='openbb_terminal/portfolio/portfolio_view.py'
def display_distribution_returns(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, window: str, raw: bool, export: str, external_axes: Optional[matplotlib.axes._axes.Axes]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L539)

Description: Display daily returns

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_returns | pd.Series | Returns of the portfolio | None | False |
| benchmark_returns | pd.Series | Returns of the benchmark | None | False |
| interval | str | interval to compare cumulative returns and benchmark | None | False |
| raw | False | Display raw data from cumulative return | None | False |
| export | str | Export certain type of data | None | False |
| external_axes | plt.Axes | Optional axes to display plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>