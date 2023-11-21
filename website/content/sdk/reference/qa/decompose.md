---
title: decompose
description: This documentation page provides details on the 'decompose' function
  in OpenBB's quantitative analysis module. The function executes seasonal decomposition
  on a specified DataFrame, returning decomposed results and filtered dataframes for
  cycle and trend.
keywords:
- decompose
- seasonal decomposition
- quantitative analysis
- multiplicative
- dataframe
- DecomposeResult
- statsmodels
- observed
- seasonal
- trend
- residual
- weights
- cycle DataFrame
- trend DataFrame
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.decompose - Reference | OpenBB SDK Docs" />

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
