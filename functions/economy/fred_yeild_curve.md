---
title: fred_yeild_curve
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fred_yeild_curve

<Tabs>
<TabItem value="model" label="Model" default>

## economy_fred_model.get_yield_curve

```python title='openbb_terminal/decorators.py'
def get_yield_curve() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L251)

Description: Gets yield curve data from FRED

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get curve for.  If None, gets most recent date | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe of yields and maturities |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_fred_view.display_yield_curve

```python title='openbb_terminal/decorators.py'
def display_yield_curve() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L177)

Description: Display yield curve based on US Treasury rates for a specified date.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| date | datetime | Date to get yield curve for | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes to plot data on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>