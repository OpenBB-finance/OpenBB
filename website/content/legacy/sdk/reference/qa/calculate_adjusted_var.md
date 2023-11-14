---
title: calculate_adjusted_var
description: This docusaurus page explains the calculation of adjusted VaR, which
  takes into account skew and kurtosis. It includes the explanation of the source
  code, parameters used, and what the function returns.
keywords:
- Docusaurus page
- adjusted VaR calculation
- Cornish-Fischer-Expansion
- quantitative analysis
- Python code
- source code explanation
- kurtosis
- skew
- standard deviation
- mean
- normal distribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="qa.calculate_adjusted_var - Reference | OpenBB SDK Docs" />

Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L182)]

```python
openbb.qa.calculate_adjusted_var(kurtosis: float, skew: float, ndp: float, std: float, mean: float)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| kurtosis | float | kurtosis of data | None | False |
| skew | float | skew of data | None | False |
| ndp | float | normal distribution percentage number (99% -> -2.326) | None | False |
| std | float | standard deviation of data | None | False |
| mean | float | mean of data | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | Real adjusted VaR |
---
