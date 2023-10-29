---
title: curve
description: The documentation page provides detailed instructions on how to retrieve
  and display curve futures using the OpenBB Python library, with source code provided.
  The API functions interact with data from Yahoo Finance and include customization
  options for data representation and export format.
keywords:
- curve futures
- Yahoo Finance
- futures data
- data visualization
- matplotlib
- API documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="futures.curve - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get curve futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_model.py#L118)]

```python
openbb.futures.curve(symbol: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | symbol to get forward curve |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dictionary with sector weightings allocation |
---

</TabItem>
<TabItem value="view" label="Chart">

Display curve futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_view.py#L232)]

```python
openbb.futures.curve_chart(symbol: str, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Curve future symbol to display | None | False |
| raw | bool | Display futures timeseries in raw format | False | True |
| export | str | Type of format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
