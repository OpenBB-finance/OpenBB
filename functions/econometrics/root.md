---
title: root
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# root

<Tabs>
<TabItem value="model" label="Model" default>

## econometrics_model.get_root

```python title='openbb_terminal/econometrics/econometrics_model.py'
def get_root(data: pd.Series, fuller_reg: str, kpss_reg: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L166)

Description: Calculate test statistics for unit roots

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series or column of DataFrame of target variable | None | False |
| fuller_reg | str | Type of regression of ADF test | None | False |
| kpss_reg | str | Type of regression for KPSS test | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with results of ADF test and KPSS test |

## Examples



</TabItem>
<TabItem value="view" label="View">

## econometrics_view.display_root

```python title='openbb_terminal/econometrics/econometrics_view.py'
def display_root(data: pd.Series, dataset: str, column: str, fuller_reg: str, kpss_reg: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L204)

Description: Determine the normality of a timeseries.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of target variable | None | False |
| dataset | str | Name of the dataset | None | False |
| column | str | Name of the column | None | False |
| fuller_reg | str | Type of regression of ADF test. Choose c, ct, ctt, or nc | None | False |
| kpss_reg | str | Type of regression for KPSS test. Choose c or ct | None | False |
| export | str | Format to export data. | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>