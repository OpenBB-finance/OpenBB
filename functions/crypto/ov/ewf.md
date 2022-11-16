---
title: ewf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ewf

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_withdrawalfees_model.get_overall_exchange_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py'
def get_overall_exchange_withdrawal_fees() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L181)

Description: Scrapes exchange withdrawal fees

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Exchange, Coins, Lowest, Average, Median, Highest |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_withdrawalfees_view.display_overall_exchange_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py'
def display_overall_exchange_withdrawal_fees(export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L53)

Description: Exchange withdrawal fees

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>