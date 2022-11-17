---
title: rsharpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rsharpe

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_model.get_rolling_sharpe

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_rolling_sharpe(portfolio: pd.DataFrame, risk_free_rate: float, window: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1471)

Description: Get rolling sharpe ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio_returns | pd.Series | Series of portfolio returns | None | False |
| risk_free_rate | float | Risk free rate | None | False |
| window | str | Rolling window to use
Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rolling sharpe ratio DataFrame |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_view.display_rolling_sharpe

```python title='openbb_terminal/portfolio/portfolio_view.py'
def display_rolling_sharpe(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, risk_free_rate: float, window: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L843)

Description: Display rolling sharpe

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | PortfolioModel | Portfolio object | None | False |
| risk_free_rate | float | Value to use for risk free rate in sharpe/other calculations | None | False |
| window | str | interval for window to consider | None | False |
| export | str | Export to file | None | False |
| external_axes | Optional[List[plt.Axes]] | Optional axes to display plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>