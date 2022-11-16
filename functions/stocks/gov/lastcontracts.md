---
title: lastcontracts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# lastcontracts

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_gov_quiverquant_model.get_last_contracts

```python title='openbb_terminal/stocks/government/quiverquant_model.py'
def get_last_contracts(past_transaction_days: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_model.py#L377)

Description: Get last government contracts [Source: quiverquant.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of government contracts |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_gov_quiverquant_view.display_last_contracts

```python title='openbb_terminal/stocks/government/quiverquant_view.py'
def display_last_contracts(past_transaction_days: int, limit: int, sum_contracts: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/government/quiverquant_view.py#L225)

Description: Last government contracts [Source: quiverquant.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| past_transaction_days | int | Number of days to look back | None | False |
| limit | int | Number of contracts to show | None | False |
| sum_contracts | bool | Flag to show total amount of contracts given out. | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>