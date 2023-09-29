---
title: cdf
description: OpenBB SDK Function
---

# cdf

Plots Cumulative Distribution Function

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L159)]

```python
openbb.qa.cdf(data: pd.DataFrame, target: str, symbol: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe to look at | None | False |
| target | str | Data column | None | False |
| symbol | str | Name of dataset |  | True |
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
openbb.qa.cdf(data=df, target="Adj Close")
```

---

