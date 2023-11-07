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

Get historical futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_model.py#L79)]

```python
openbb.futures.historical(symbols: List[str], expiry: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of future timeseries symbols to display | None | False |
| expiry | str | Future expiry date with format YYYY-MM |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dictionary with sector weightings allocation |
---

</TabItem>
<TabItem value="view" label="Chart">

Display historical futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_view.py#L65)]

```python
openbb.futures.historical_chart(symbols: List[str], expiry: str = "", start_date: Optional[str] = None, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | List[str] | List of future timeseries symbols to display | None | False |
| expiry | str | Future expiry date with format YYYY-MM |  | True |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| raw | bool | Display futures timeseries in raw format | False | True |
| export | str | Type of format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
