---
title: unitroot
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# unitroot

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_unitroot

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_unitroot(data: pd.DataFrame, fuller_reg: str, kpss_reg: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L137)

Description: Calculate test statistics for unit roots

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of target variable | None | False |
| fuller_reg | str | Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order | None | False |
| kpss_reg | str | Type of regression for KPSS test.  Can be ‘c’,’ct' | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with results of ADF test and KPSS test |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_unitroot

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_unitroot(data: pd.DataFrame, target: str, fuller_reg: str, kpss_reg: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L803)

Description: Show unit root test calculations

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame | None | False |
| target | str | Column of data to look at | None | False |
| fuller_reg | str | Type of regression of ADF test. Can be ‘c’,’ct’,’ctt’,’nc’ 'c' - Constant and t - trend order | None | False |
| kpss_reg | str | Type of regression for KPSS test. Can be ‘c’,’ct' | None | False |
| export | str | Format for exporting data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>