---
title: load
description: Learn how to use the load function within OpenBBTerminal's stocks module
  to retrieve and analyze data. Provide a symbol (ticker), define start and end dates,
  interval, choose whether to include pre/post-hours data and the data source. Options
  to retrieve weekly and monthly data are available. The gathered data is returned
  as a pandas DataFrame.
keywords:
- symbol analysis
- start_date
- interval
- end_date
- prepost
- source
- YahooFinance
- weekly data
- monthly data
- verbose
- data extraction
- dataframe
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.load - Reference | OpenBB SDK Docs" />

Load a symbol to perform analysis using the string above as a template.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/stocks_helper.py#L223)]

```python
openbb.stocks.load(symbol: str, start_date: Union[datetime.datetime, str, NoneType] = None, interval: int = 1440, end_date: Union[datetime.datetime, str, NoneType] = None, prepost: bool = False, source: str = "YahooFinance", weekly: bool = False, monthly: bool = False, verbose: bool = True)
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
| weekly | bool | Flag to get weekly data | False | True |
| monthly | bool | Flag to get monthly data | False | True |
| verbose | bool | Display verbose information on what was the symbol that was loaded | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of data |
---
