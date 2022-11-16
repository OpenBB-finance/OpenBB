---
title: holdv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# holdv

<Tabs>
<TabItem value="model" label="Model" default>

## portfolio_model.get_holdings_value

```python title='openbb_terminal/portfolio/portfolio_model.py'
def get_holdings_value(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_model.py#L1339)

Description: Get holdings of assets (absolute value)

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of holdings |

## Examples



</TabItem>
<TabItem value="view" label="View">

## portfolio_view.display_holdings_value

```python title='openbb_terminal/portfolio/portfolio_view.py'
def display_holdings_value(portfolio: openbb_terminal.portfolio.portfolio_model.PortfolioModel, unstack: bool, raw: bool, limit: int, export: str, external_axes: Optional[matplotlib.axes._axes.Axes]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/portfolio/portfolio_view.py#L626)

Description: Display holdings of assets (absolute value)

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| portfolio | Portfolio | Portfolio object with trades loaded | None | False |
| unstack | bool | Individual assets over time | None | False |
| raw | bool | To display raw data | None | False |
| limit | int | Number of past market days to display holdings | None | False |
| export | str | Format to export plot | None | False |
| external_axes | plt.Axes | Optional axes to display plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>