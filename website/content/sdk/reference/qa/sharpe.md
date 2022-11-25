---
title: sharpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sharpe

<Tabs>
<TabItem value="model" label="Model" default>

Calculates the sharpe ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L537)]

```python
openbb.qa.sharpe(data: pd.DataFrame, rfr: float = 0, window: float = 252)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe column | None | False |
| rfr | float | risk free rate | 0 | True |
| window | float | length of the rolling window | 252 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | sharpe ratio |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots Calculated the sharpe ratio

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1156)]

```python
openbb.qa.sharpe_chart(data: pd.DataFrame, rfr: float = 0, window: float = 252)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe column | None | False |
| rfr | float | risk free rate | 0 | True |
| window | float | length of the rolling window | 252 | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>