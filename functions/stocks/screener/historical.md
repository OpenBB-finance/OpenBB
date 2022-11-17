---
title: historical
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# historical

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_screener_yahoofinance_model.historical

```python title='openbb_terminal/stocks/screener/yahoofinance_model.py'
def historical(preset_loaded: str, limit: int, start_date: str, type_candle: str, normalize: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/yahoofinance_model.py#L53)

Description: View historical price of stocks that meet preset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Preset loaded to filter for tickers | None | False |
| limit | int | Number of stocks to display | None | False |
| start_date | str | Start date to display historical data, in YYYY-MM-DD format | None | False |
| type_candle | str | Type of candle to display | None | False |
| normalize | bool | Boolean to normalize all stock prices using MinMax | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of the screener |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_screener_yahoofinance_view.historical

```python title='openbb_terminal/stocks/screener/yahoofinance_view.py'
def historical(preset_loaded: str, limit: int, start_date: str, type_candle: str, normalize: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/screener/yahoofinance_view.py#L28)

Description: View historical price of stocks that meet preset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| preset_loaded | str | Preset loaded to filter for tickers | None | False |
| limit | int | Number of stocks to display | None | False |
| start_date | str | Start date to display historical data, in YYYY-MM-DD format | None | False |
| type_candle | str | Type of candle to display | None | False |
| normalize | bool | Boolean to normalize all stock prices using MinMax | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

| Type | Description |
| ---- | ----------- |
| list[str] | List of stocks |

## Examples



</TabItem>
</Tabs>