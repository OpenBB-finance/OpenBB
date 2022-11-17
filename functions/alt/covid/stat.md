---
title: stat
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stat

<Tabs>
<TabItem value="model" label="Model" default>

## alt_covid_model.get_covid_stat

```python title='openbb_terminal/alternative/covid/covid_model.py'
def get_covid_stat(country: str, stat: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L121)

Description: Show historical cases and deaths by country

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |
| stat | str | Statistic to get.  Either "cases", "deaths" or "rates" | None | False |
| limit | int | Number of raw data to show | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## alt_covid_view.display_covid_stat

```python title='openbb_terminal/alternative/covid/covid_view.py'
def display_covid_stat(country: str, stat: str, raw: bool, limit: int, export: str, plot: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_view.py#L172)

Description: Show historical cases and deaths by country

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |
| stat | str | Statistic to get.  Either "cases", "deaths" or "rates" | None | False |
| raw | bool | Flag to display raw data | None | False |
| limit | int | Number of raw data to show | None | False |
| export | str | Format to export data | None | False |
| plot | bool | Flag to plot data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>