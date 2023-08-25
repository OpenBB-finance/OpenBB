---
title: line
description: OpenBB SDK Function
---

# line

Display line plot of data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L938)]

```python
openbb.qa.line(data: pd.Series, title: str = "", log_y: bool = True, markers_lines: Optional[List[datetime.datetime]] = None, markers_scatter: Optional[List[datetime.datetime]] = None, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Data to plot | None | False |
| title | str | Title for plot |  | True |
| log_y | bool | Flag for showing y on log scale | True | True |
| markers_lines | Optional[List[datetime]] | List of dates to highlight using vertical lines | None | True |
| markers_scatter | Optional[List[datetime]] | List of dates to highlight using scatter | None | True |
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
openbb.qa.line(data=df["Adj Close"])
```

---

