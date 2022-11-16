---
title: decompose
description: OpenBB SDK Function
---

# decompose

## common_qa_model.get_seasonal_decomposition

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_seasonal_decomposition(data: pd.DataFrame, multiplicative: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L46)

Description: Perform seasonal decomposition

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |
| multiplicative | bool | Boolean to indicate multiplication instead of addition | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Any | Result of statsmodels seasonal_decompose |

## Examples

