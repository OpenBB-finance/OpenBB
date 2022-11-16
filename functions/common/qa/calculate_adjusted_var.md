---
title: calculate_adjusted_var
description: OpenBB SDK Function
---

# calculate_adjusted_var

## common_qa_model.calculate_adjusted_var

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def calculate_adjusted_var(kurtosis: float, skew: float, ndp: float, std: float, mean: float) -> float:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L184)

Description: Calculates VaR, which is adjusted for skew and kurtosis (Cornish-Fischer-Expansion)

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| kurtosis | float | kurtosis of data | None | False |
| skew | float | skew of data | None | False |
| ndp | float | normal distribution percentage number (99% -> -2.326) | None | False |
| std | float | standard deviation of data | None | False |
| mean | float | mean of data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| float | Real adjusted VaR |

## Examples

