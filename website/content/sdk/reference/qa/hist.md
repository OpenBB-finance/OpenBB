---
title: hist
description: This page provides a detailed guide on the usage of the 'openbb.qa.hist'
  function from OpenBB. This function is utilized for plotting histograms of data,
  particularly from a Pandas DataFrame. It also includes parameters, returns, and
  examples for a better understanding.
keywords:
- Histogram
- Quantitative Analysis
- Data Visualization
- Pandas DataFrame
- openbb.qa.hist function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.hist - Reference | OpenBB SDK Docs" />

Plots histogram of data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L82)]

```python
openbb.qa.hist(data: pd.DataFrame, target: str, symbol: str = "", bins: int = 15, external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe to look at | None | False |
| target | str | Data column to get histogram of the dataframe | None | False |
| symbol | str | Name of dataset |  | True |
| bins | int | Number of bins in histogram | 15 | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.stocks.load("AAPL")
openbb.qa.hist(data=df, target="Adj Close")
```

---
