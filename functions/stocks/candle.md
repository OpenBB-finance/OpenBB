---
title: candle
description: OpenBB SDK Function
---

# candle

## stocks_helper.display_candle

```python title='openbb_terminal/stocks/stocks_helper.py'
def display_candle(symbol: str, data: pd.DataFrame, use_matplotlib: bool, intraday: bool, add_trend: bool, ma: Optional[Iterable[int]], asset_type: str, start_date: Union[datetime.datetime, str, NoneType], interval: int, end_date: Union[datetime.datetime, str, NoneType], prepost: bool, source: str, iexrange: str, weekly: bool, monthly: bool, external_axes: Optional[List[matplotlib.axes._axes.Axes]], raw: bool, yscale: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L433)

Description: Show candle plot of loaded ticker.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker name | None | False |
| data | pd.DataFrame | Stock dataframe | None | False |
| use_matplotlib | bool | Flag to use matplotlib instead of interactive plotly chart | None | False |
| intraday | bool | Flag for intraday data for plotly range breaks | None | False |
| add_trend | bool | Flag to add high and low trends to chart | None | False |
| ma | Tuple[int] | Moving averages to add to the candle | None | False |
| asset_type_ | str | String to include in title | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |
| asset_type_ | str | String to include in title | None | False |
| start_date | str or datetime | Start date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| interval | int | Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440 | None | False |
| end_date | str or datetime | End date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| prepost | bool | Pre and After hours data | None | False |
| source | str | Source of data extracted | None | False |
| iexrange | str | Timeframe to get IEX data. | None | False |
| weekly | bool | Flag to get weekly data | None | False |
| monthly | bool | Flag to get monthly data | None | False |
| raw | bool | Flag to display raw data, by default False | False | True |
| yscale | str | Linear or log for yscale | None | False |

## Returns

This function does not return anything

## Examples

