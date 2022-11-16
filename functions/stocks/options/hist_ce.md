---
title: hist_ce
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hist_ce

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_chartexchange_model.get_option_history

```python title='openbb_terminal/stocks/options/chartexchange_model.py'
def get_option_history(symbol: str, date: str, call: bool, price: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/chartexchange_model.py#L19)

Description: Historic prices for a specific option [chartexchange]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get historical data from | None | False |
| date | str | Date as a string YYYYMMDD | None | False |
| call | bool | Whether to show a call or a put | None | False |
| price | str | Strike price for a specific option | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Historic information for an option |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_chartexchange_view.display_raw

```python title='openbb_terminal/stocks/options/chartexchange_view.py'
def display_raw(symbol: str, expiry: str, call: bool, price: float, limit: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/chartexchange_view.py#L59)

Description: Return raw stock data[chartexchange]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol for the given option | None | False |
| expiry | str | The expiry of expiration, format "YYYY-MM-DD", i.e. 2010-12-31. | None | False |
| call | bool | Whether the underlying asset should be a call or a put | None | False |
| price | float | The strike of the expiration | None | False |
| limit | int | Number of rows to show | None | False |
| export | str | Export data as CSV, JSON, XLSX | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>