---
title: candle
description: OpenBB SDK Function
---

# candle

Show candle plot of loaded ticker.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L443)]

```python
openbb.etf.candle(symbol: str, data: pd.DataFrame = None, use_matplotlib: bool = True, intraday: bool = False, add_trend: bool = False, ma: Optional[Iterable[int]] = None, asset_type: str = "", start_date: Union[datetime.datetime, str, NoneType] = None, interval: int = 1440, end_date: Union[datetime.datetime, str, NoneType] = None, prepost: bool = False, source: str = "YahooFinance", iexrange: str = "ytd", weekly: bool = False, monthly: bool = False, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None, raw: bool = False, yscale: str = "linear")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker name | None | False |
| data | pd.DataFrame | Stock dataframe | None | True |
| use_matplotlib | bool | Flag to use matplotlib instead of interactive plotly chart | True | True |
| intraday | bool | Flag for intraday data for plotly range breaks | False | True |
| add_trend | bool | Flag to add high and low trends to chart | False | True |
| ma | Tuple[int] | Moving averages to add to the candle | None | True |
| asset_type_ | str | String to include in title | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |
| asset_type_ | str | String to include in title | None | True |
| start_date | str or datetime | Start date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| interval | int | Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440 | 1440 | True |
| end_date | str or datetime | End date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| prepost | bool | Pre and After hours data | False | True |
| source | str | Source of data extracted | YahooFinance | True |
| iexrange | str | Timeframe to get IEX data. | ytd | True |
| weekly | bool | Flag to get weekly data | False | True |
| monthly | bool | Flag to get monthly data | False | True |
| raw | bool | Flag to display raw data, by default False | False | True |
| yscale | str | Linear or log for yscale | linear | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.candle("AAPL")
```

---

