---
title: ma
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ma

<Tabs>
<TabItem value="model" label="Model" default>

Plots MA technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_view.py#L32)]

```python
openbb.ta.ma(data: pd.Series, window: List[int] = None, offset: int = 0, ma_type: str = "EMA", symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of prices | None | False |
| window | List[int] | Length of EMA window | None | True |
| offset | int | Offset variable | 0 | True |
| ma_type | str | Type of moving average.  Either "EMA" "ZLMA" or "SMA" | EMA | True |
| symbol | str | Ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.ma_chart(data=df["Adj Close"], symbol="AAPL", ma_type="EMA", window=[20, 50, 100])
```

```python
from openbb_terminal.sdk import openbb
spuk_index = openbb.economy.index(indices = ["^SPUK"])
openbb.ta.ma_chart(data = spuk_index["^SPUK"], symbol = "S&P UK Index", ma_type = "EMA", window = [20, 50, 100])
```

---



</TabItem>
<TabItem value="view" label="Chart">

Plots MA technical indicator

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_view.py#L32)]

```python
openbb.ta.ma_chart(data: pd.Series, window: List[int] = None, offset: int = 0, ma_type: str = "EMA", symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of prices | None | False |
| window | List[int] | Length of EMA window | None | True |
| offset | int | Offset variable | 0 | True |
| ma_type | str | Type of moving average.  Either "EMA" "ZLMA" or "SMA" | EMA | True |
| symbol | str | Ticker |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.ta.ma_chart(data=df["Adj Close"], symbol="AAPL", ma_type="EMA", window=[20, 50, 100])
```

```python
from openbb_terminal.sdk import openbb
spuk_index = openbb.economy.index(indices = ["^SPUK"])
openbb.ta.ma_chart(data = spuk_index["^SPUK"], symbol = "S&P UK Index", ma_type = "EMA", window = [20, 50, 100])
```

---



</TabItem>
</Tabs>