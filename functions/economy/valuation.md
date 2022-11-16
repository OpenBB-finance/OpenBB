---
title: valuation
description: OpenBB SDK Function
---

# valuation

## economy_finviz_model.get_valuation_data

```python title='openbb_terminal/economy/finviz_model.py'
def get_valuation_data(group: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L66)

Description: Get group (sectors, industry or country) valuation data. [Source: Finviz]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | Group by category. Available groups can be accessed through get_groups(). | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Flag to sort in ascending order | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| pd.DataFrame | None | dataframe with valuation/performance data | None | None |

## Returns

This function does not return anything

## Examples

