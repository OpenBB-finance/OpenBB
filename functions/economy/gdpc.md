---
title: gdpc
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# gdpc

<Tabs>
<TabItem value="model" label="Model" default>

## economy_alphavantage_model.get_gdp_capita

```python title='openbb_terminal/economy/alphavantage_model.py'
def get_gdp_capita(start_year: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L95)

Description: Real GDP per Capita for United States

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of GDP per Capita |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_alphavantage_view.display_gdp_capita

```python title='openbb_terminal/decorators.py'
def display_gdp_capita() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L146)

Description: Display US GDP per Capita from AlphaVantage

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |
| raw | bool | Flag to show raw data, by default False | False | True |
| export | str | Format to export data, by default | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>