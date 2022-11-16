---
title: whales
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# whales

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_whale_alert_model.get_whales_transactions

```python title='openbb_terminal/cryptocurrency/onchain/whale_alert_model.py'
def get_whales_transactions(min_value: int, limit: int, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/whale_alert_model.py#L86)

Description: Whale Alert's API allows you to retrieve live and historical transaction data from major blockchains.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| min_value | int | Minimum value of trade to track. | None | False |
| limit | int | Limit of transactions. Max 100 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in ascending order. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Crypto wales transactions |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_whale_alert_view.display_whales_transactions

```python title='openbb_terminal/decorators.py'
def display_whales_transactions() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L21)

Description: Display huge value transactions from major blockchains. [Source: https://docs.whale-alert.io/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| min_value | int | Minimum value of trade to track. | None | False |
| limit | int | Limit of transactions. Maximum 100 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in ascending order. | None | False |
| show_address | bool | Flag to show addresses of transactions. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>