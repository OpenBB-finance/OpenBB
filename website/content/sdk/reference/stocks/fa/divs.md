---
title: divs
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# divs

<Tabs>
<TabItem value="model" label="Model" default>

Get historical dividend for ticker

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_model.py#L256)]

```python
openbb.stocks.fa.divs(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get dividend for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of dividends and dates |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.fa.divs("AAPL")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display historical dividends

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/yahoo_finance_view.py#L185)]

```python
openbb.stocks.fa.divs_chart(symbol: str, limit: int = 12, plot: bool = True, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number to show | 12 | True |
| plot | bool | Plots historical data | True | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.fa.divs_chart("AAPL")
```

---



</TabItem>
</Tabs>