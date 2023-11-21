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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_model.py#L154)]

```python wordwrap
openbb.futures.curve(symbol: str = "", date: Optional[str] = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | symbol to get forward curve |  | True |
| date | str | optionally include historical price for each contract |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dictionary with sector weightings allocation |
---



</TabItem>
<TabItem value="view" label="Chart">

Display curve futures [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/futures/yfinance_view.py#L194)]

```python wordwrap
openbb.futures.curve_chart(symbol: str, date: Optional[str] = "", raw: bool = False, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Curve future symbol to display | None | False |
| date | str | Optionally include historical futures prices for each contract |  | True |
| raw | bool | Display futures prices in raw format | False | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Type of format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>