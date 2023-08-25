---
title: decompose
description: OpenBB SDK Function
---

# decompose

Perform seasonal decomposition

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L46)]

```python
openbb.qa.decompose(data: pd.DataFrame, multiplicative: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |
| multiplicative | bool | Boolean to indicate multiplication instead of addition | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[DecomposeResult, pd.DataFrame, pd.DataFrame] | DecomposeResult class from statsmodels (observed, seasonal, trend, residual, and weights),<br/>Filtered cycle DataFrame,<br/>Filtered trend DataFrame |
---

