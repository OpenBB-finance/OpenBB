---
title: historical
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# historical

<Tabs>
<TabItem value="model" label="Model" default>

## futures_yfinance_model.get_historical_futures

```python title='openbb_terminal/futures/yfinance_model.py'
def get_historical_futures(symbols: List[str], expiry: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_model.py#L79)

Description: Get historical futures [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of future timeseries symbols to display | None | False |
| expiry | str | Future expiry date with format YYYY-MM | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dictionary with sector weightings allocation |

## Examples



</TabItem>
<TabItem value="view" label="View">

## futures_yfinance_view.display_historical

```python title='openbb_terminal/futures/yfinance_view.py'
def display_historical(symbols: List[str], expiry: str, start_date: str, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_view.py#L65)

Description: Display historical futures [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of future timeseries symbols to display | None | False |
| expiry | str | Future expiry date with format YYYY-MM | None | False |
| start_date | str | Initial date like string (e.g., 2021-10-01) | None | False |
| raw | bool | Display futures timeseries in raw format | None | False |
| export | str | Type of format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>