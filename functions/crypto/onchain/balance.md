---
title: balance
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# balance

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_ethplorer_model.get_address_info

```python title='openbb_terminal/cryptocurrency/onchain/ethplorer_model.py'
def get_address_info(address: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L196)

Description: Get info about tokens on you ethereum blockchain balance. Eth balance, balance of all tokens which

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Blockchain balance e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in descending order. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | DataFrame with list of tokens and their balances. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_ethplorer_view.display_address_info

```python title='openbb_terminal/decorators.py'
def display_address_info() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L21)

Description: Display info about tokens for given ethereum blockchain balance e.g. ETH balance,

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Ethereum balance. | None | False |
| limit | int | Limit of transactions. Maximum 100 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in descending order. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>