---
title: ftd
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ftd

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dps_sec_model.get_fails_to_deliver

```python title='openbb_terminal/stocks/dark_pool_shorts/sec_model.py'
def get_fails_to_deliver(symbol: str, start_date: str, end_date: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/sec_model.py#L59)

Description: Display fails-to-deliver data for a given ticker. [Source: SEC]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| start_date | str | Start of data, in YYYY-MM-DD format | None | False |
| end_date | str | End of data, in YYYY-MM-DD format | None | False |
| limit | int | Number of latest fails-to-deliver being printed | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Fail to deliver data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dps_sec_view.fails_to_deliver

```python title='openbb_terminal/stocks/dark_pool_shorts/sec_view.py'
def fails_to_deliver(symbol: str, data: pd.DataFrame, start_date: str, end_date: str, limit: int, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/sec_view.py#L27)

Description: Display fails-to-deliver data for a given ticker. [Source: SEC]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| data | pd.DataFrame | Stock data | None | False |
| start_date | str | Start of data, in YYYY-MM-DD format | None | False |
| end_date | str | End of data, in YYYY-MM-DD format | None | False |
| limit | int | Number of latest fails-to-deliver being printed | None | False |
| raw | bool | Print raw data | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>