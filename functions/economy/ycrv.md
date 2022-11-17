---
title: ycrv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ycrv

<Tabs>
<TabItem value="model" label="Model" default>

## economy_investingcom_model.get_yieldcurve

```python title='openbb_terminal/economy/investingcom_model.py'
def get_yieldcurve(country: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/investingcom_model.py#L306)

Description: Get yield curve for specified country. [Source: Investing.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to display yield curve. List of available countries is accessible through get_ycrv_countries(). | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Country yield curve |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_investingcom_view.display_yieldcurve

```python title='openbb_terminal/economy/investingcom_view.py'
def display_yieldcurve(country: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]], raw: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/investingcom_view.py#L208)

Description: Display yield curve for specified country. [Source: Investing.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to display yield curve. List of available countries is accessible through get_ycrv_countries(). | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>