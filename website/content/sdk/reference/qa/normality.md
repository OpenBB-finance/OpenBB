---
title: normality
description: This page provides detailed information on OpenBB's qa.normality and
  qa.normality_chart functions used for quantitative analysis. These functions are
  used to generate statistics on the relation to the normal curve, targeting specific
  data in a dataframe.
keywords:
- openbb.qa.normality
- quantitative analysis
- distribution returns
- normal curve
- openbb.qa.normality_chart
- dataframe
- statistics normality
- targeted data
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.normality - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Look at the distribution of returns and generate statistics on the relation to the normal curve.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L81)]

```python
openbb.qa.normality(data: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing statistics of normality |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing normality statistics

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L805)]

```python
openbb.qa.normality_chart(data: pd.DataFrame, target: str, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame | None | False |
| target | str | Column in data to look at | None | False |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
