---
title: cusum
description: OpenBB SDK Function
---

# cusum

Plots Cumulative sum algorithm (CUSUM) to detect abrupt changes in data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L523)]

```python
openbb.qa.cusum(data: pd.DataFrame, target: str, threshold: float = 5, drift: float = 2.1, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column of data to look at | None | False |
| threshold | float | Threshold value | 5 | True |
| drift | float | Drift parameter | 2.1 | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.qa.cusum(data=df, target="Adj Close")
```

---

