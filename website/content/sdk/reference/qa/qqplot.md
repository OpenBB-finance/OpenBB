---
title: qqplot
description: The 'qqplot' page provides information on how to use the 'qqplot' function
  in the OpenBB library for quantitative data analysis. It explains the procedure,
  the parameters required, and provides a practical example using the stock ticker
  from Apple.
keywords:
- qqplot
- quantitative analysis
- data analysis
- matplotlib
- Pandas Dataframe
- stock ticker
- AAPL
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.qqplot - Reference | OpenBB SDK Docs" />

Plots QQ plot for data against normal quantiles

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L400)]

```python wordwrap
openbb.qa.qqplot(data: pd.DataFrame, target: str, symbol: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


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

