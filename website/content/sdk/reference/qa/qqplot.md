---
title: qqplot
description: OpenBB SDK Function
---

# qqplot

Plots QQ plot for data against normal quantiles

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L462)]

```python
openbb.qa.qqplot(data: pd.DataFrame, target: str, symbol: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.qa.qqplot(data=df, target="Adj Close")
```

---

