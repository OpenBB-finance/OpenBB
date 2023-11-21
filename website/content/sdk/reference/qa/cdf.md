---
title: cdf
description: The page provides details about the 'cdf' function in the OpenBB SDK,
  which plots the Cumulative Distribution Function. It lists the function parameters,
  return values, and provides a working example.
keywords:
- Cumulative Distribution Function
- Quantitative Analysis
- OpenBB SDK
- clf function
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.cdf - Reference | OpenBB SDK Docs" />

Plots Cumulative Distribution Function

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L141)]

```python wordwrap
openbb.qa.cdf(data: pd.DataFrame, target: str, symbol: str = "", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe to look at | None | False |
| target | str | Data column | None | False |
| symbol | str | Name of dataset |  | True |
| export | str | Format to export data |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


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

