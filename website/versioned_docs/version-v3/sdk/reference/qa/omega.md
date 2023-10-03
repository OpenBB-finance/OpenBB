---
title: omega
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# omega

<Tabs>
<TabItem value="model" label="Model" default>

Get the omega series

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L639)]

```python
openbb.qa.omega(data: pd.DataFrame, threshold_start: float = 0, threshold_end: float = 1.5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | stock dataframe | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | 0 | True |
| threshold_end | float | annualized target return threshold end of plotted threshold range | 1.5 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | omega series |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots the omega ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1214)]

```python
openbb.qa.omega_chart(data: pd.DataFrame, threshold_start: float = 0, threshold_end: float = 1.5)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | stock dataframe | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | 0 | True |
| threshold_end | float | annualized target return threshold end of plotted threshold range | 1.5 | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>