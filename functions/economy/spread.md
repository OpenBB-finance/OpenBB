---
title: spread
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# spread

<Tabs>
<TabItem value="model" label="Model" default>

## economy_investingcom_model.get_spread_matrix

```python title='openbb_terminal/economy/investingcom_model.py'
def get_spread_matrix(countries: Union[str, List[str]], maturity: str, change: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/investingcom_model.py#L224)

Description: Get spread matrix. [Source: Investing.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | Union[str, List[str]] | Countries or group of countries. List of available countries is accessible through get_ycrv_countries(). | None | False |
| maturity | str | Maturity to get data. By default 10Y. | 10Y | False |
| change | bool | Flag to use 1 day change or not. By default False. | False | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Spread matrix. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_investingcom_view.display_spread_matrix

```python title='openbb_terminal/economy/investingcom_view.py'
def display_spread_matrix(countries: Union[str, List[str]], maturity: str, change: bool, color: str, raw: bool, external_axes: Optional[List[matplotlib.axes._axes.Axes]], export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/investingcom_view.py#L39)

Description: Display spread matrix. [Source: Investing.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | Union[str, List[str]] | Countries or group of countries. List of available countries is accessible through get_ycrv_countries(). | None | False |
| maturity | str | Maturity to get data. By default 10Y. | 10Y | False |
| change | bool | Flag to use 1 day change or not. By default False. | False | False |
| color | str | Color theme to use on heatmap, from rgb, binary or openbb By default, openbb. | None | False |
| raw | bool | Output only raw data. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>