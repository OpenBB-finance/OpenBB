---
title: vsurf
description: A documentation page that guides how to use vsurf method which gets the
  IV surface for calls and puts for stock ticker symbol and how to utilize vsurf_chart
  to display the vol surface. Includes source code, data types and defaults.
keywords:
- Docusaurus
- vSurf
- vSurf_Chart
- IV Surface
- vol surface
- options
- ticker symbol
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.vsurf - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gets IV surface for calls and puts for ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L263)]

```python wordwrap
openbb.stocks.options.vsurf(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol to get | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of DTE, Strike and IV |
---



</TabItem>
<TabItem value="view" label="Chart">

Display vol surface

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_view.py#L256)]

```python wordwrap
openbb.stocks.options.vsurf_chart(symbol: str, export: str = "", sheet_name: Optional[str] = None, z: str = "IV", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get surface for | None | False |
| export | str | Format to export data |  | True |
| z | str | The variable for the Z axis | IV | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>