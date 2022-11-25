---
title: clenow
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# clenow

<Tabs>
<TabItem value="model" label="Model" default>

Gets the Clenow Volatility Adjusted Momentum.  this is defined as the regression coefficient on log prices

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L207)]

```python
openbb.ta.clenow(values: pd.Series, window: int = 90)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| values | pd.Series | Values to perform regression for | None | False |
| window | int | Length of lookback period | 90 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
|  | R2 of fit to log data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.clenow(df["Close"])
```

---



</TabItem>
<TabItem value="view" label="Chart">

Prints table and plots clenow momentum

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_view.py#L570)]

```python
openbb.ta.clenow_chart(data: pd.Series, symbol: str = "", window: int = 90, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of values | None | False |
| symbol | str | Symbol that the data corresponds to |  | True |
| window | int | Length of window | 90 | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.clenow_chart(df["Close"])
```

---



</TabItem>
</Tabs>