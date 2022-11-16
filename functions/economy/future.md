---
title: future
description: OpenBB SDK Function
---

# future

## economy_finviz_model.get_futures

```python title='openbb_terminal/economy/finviz_model.py'
def get_futures(future_type: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L187)

Description: Get futures data. [Source: Finviz]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| future_type | str | From the following: Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Flag to sort in ascending order | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| pd.Dataframe | None | Indices, Energy, Metals, Meats, Grains, Softs, Bonds, Currencies | None | None |

## Returns

This function does not return anything

## Examples

