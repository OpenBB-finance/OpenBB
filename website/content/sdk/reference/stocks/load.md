---
title: load
description: OpenBB SDK Function
---

# load

Load a symbol to perform analysis using the string above as a template.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L223)]

```python
openbb.stocks.load(symbol: str, start_date: Union[datetime.datetime, str, NoneType] = None, interval: int = 1440, end_date: Union[datetime.datetime, str, NoneType] = None, prepost: bool = False, source: str = "YahooFinance", iexrange: str = "ytd", weekly: bool = False, monthly: bool = False, verbose: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get data | None | False |
| start_date | str or datetime | Start date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| interval | int | Interval (in minutes) to get data 1, 5, 15, 30, 60 or 1440 | 1440 | True |
| end_date | str or datetime | End date to get data from with. - datetime or string format (YYYY-MM-DD) | None | True |
| prepost | bool | Pre and After hours data | False | True |
| source | str | Source of data extracted | YahooFinance | True |
| iexrange | str | Timeframe to get IEX data. | ytd | True |
| weekly | bool | Flag to get weekly data | False | True |
| monthly | bool | Flag to get monthly data | False | True |
| verbose | bool | Display verbose information on what was the symbol that was loaded | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of data |
---

