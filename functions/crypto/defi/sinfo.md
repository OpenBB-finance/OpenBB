---
title: sinfo
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sinfo

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_terramoney_fcd_model.get_staking_account_info

```python title='openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py'
def get_staking_account_info(address: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_model.py#L104)

Description: Get staking info for provided terra account [Source: https://fcd.terra.dev/swagger]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | luna delegations and summary report for given address |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_terramoney_fcd_view.display_account_staking_info

```python title='openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py'
def display_account_staking_info(address: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/terramoney_fcd_view.py#L32)

Description: Display staking info for provided terra account address [Source: https://fcd.terra.dev/swagger]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | terra blockchain address e.g. terra1jvwelvs7rdk6j3mqdztq5tya99w8lxk6l9hcqg | None | False |
| limit | int | Number of records to display | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>