---
title: bw
description: OpenBB SDK Function
---

# bw

Plots box and whisker plots

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L270)]

```python
openbb.qa.bw(data: pd.DataFrame, target: str, symbol: str = "", yearly: bool = True, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Name of dataset |  | True |
| data | pd.DataFrame | Dataframe to look at | None | False |
| target | str | Data column to look at | None | False |
| yearly | bool | Flag to indicate yearly accumulation | True | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.qa.bw(data=df, target="Adj Close")
```

---

