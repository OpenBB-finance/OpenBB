---
title: unitroot
description: This documentation provides in-depth information on how to calculate
  unit root test statistics, using the OpenBB software. This includes source code,
  parameter details, and return values for both model and chart functions.
keywords:
- quantitative analysis
- unit root test
- ADF test
- KPSS test
- regression
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.unitroot - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Calculate test statistics for unit roots

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L135)]

```python
openbb.qa.unitroot(data: pd.DataFrame, fuller_reg: str = "c", kpss_reg: str = "c")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of target variable | None | False |
| fuller_reg | str | Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order | c | True |
| kpss_reg | str | Type of regression for KPSS test.  Can be ‘c’,’ct' | c | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with results of ADF test and KPSS test |
---

</TabItem>
<TabItem value="view" label="Chart">

Prints table showing unit root test calculations

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L839)]

```python
openbb.qa.unitroot_chart(data: pd.DataFrame, target: str, fuller_reg: str = "c", kpss_reg: str = "c", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame | None | False |
| target | str | Column of data to look at | None | False |
| fuller_reg | str | Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order | c | True |
| kpss_reg | str | Type of regression for KPSS test. Can be ‘c’,’ct' | c | True |
| export | str | Format for exporting data |  | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
