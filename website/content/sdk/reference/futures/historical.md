---
title: historical
description: The documentation provides comprehensive details on sourcing historical
  data from Yahoo Finance using the OpenBB Python library. It covers the use of future
  timeseries symbols and the ways to display, format and export the data.
keywords:
- historical data
- Yahoo Finance
- future timeseries
- futures
- expiry date
- matplotlib.axes._axes.Axes
- export data
- raw format
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="futures.historical - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical futures data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/sdk_helper.py#L13)]

```python wordwrap
openbb.futures.historical(symbols: Union[str, List[str]], start_date: str, end_date: str, source: Optional[str] = "YahooFinance", expiry: Optional[str] = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | Union[str, List[str]] | The futures symbols you want to retrieve historical data for.<br/>It can be either a single symbol as a string or a list of symbols. | None | False |
| start_date | str | The start date of the historical data you want to retrieve. The date should be in the format "YYYY-MM-DD". | None | False |
| end_date | str | The end date of the historical data you want to retrieve. The date should be in the format "YYYY-MM-DD". | None | False |
| source | Optional[str], default "YahooFinance" | The source from which you want to retrieve the historical data.<br/>Valid values for the source are "YahooFinance" and "DataBento". | YahooFinance | True |
| expiry | Optional[str], default "" | The expiry date for futures contracts. This parameter is optional and defaults to an empty string.<br/>It is applicable only when the source is "YahooFinance" and the symbols are futures contracts. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | A pandas DataFrame containing the historical data for the given symbols and date range. |
---



</TabItem>
<TabItem value="view" label="Chart">

Display historical futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_view.py#L60)]

```python wordwrap
openbb.futures.historical_chart(symbols: List[str], expiry: str = "", start_date: Optional[str] = None, end_date: Optional[str] = None, raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of future timeseries symbols to display | None | False |
| expiry | str | Future expiry date with format YYYY-MM |  | True |
| start_date | Optional[str] | Start date of the historical data with format YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date of the historical data with format YYYY-MM-DD | None | True |
| raw | bool | Display futures timeseries in raw format | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Type of format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>