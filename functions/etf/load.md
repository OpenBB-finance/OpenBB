---
title: load
description: OpenBB SDK Function
---

# load

## stocks_helper.load

```python title='openbb_terminal/stocks/stocks_helper.py'
def load(symbol: str, start_date: Union[datetime.datetime, str, NoneType], interval: int, end_date: Union[datetime.datetime, str, NoneType], prepost: bool, source: str, iexrange: str, weekly: bool, monthly: bool, verbose: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L218)

Description: Load a symbol to perform analysis using the string above as a template.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get data | None | False |
| start_date | str or datetime | Start date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| interval | int | Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440 | None | False |
| end_date | str or datetime | End date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| prepost | bool | Pre and After hours data | None | False |
| source | str | Source of data extracted | None | False |
| iexrange | str | Timeframe to get IEX data. | None | False |
| weekly | bool | Flag to get weekly data | None | False |
| monthly | bool | Flag to get monthly data | None | False |
| verbose | bool | Display verbose information on what was the symbol that was loaded | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of data |

## Examples

