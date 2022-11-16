---
title: th
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# th

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_ethplorer_model.get_token_history

```python title='openbb_terminal/cryptocurrency/onchain/ethplorer_model.py'
def get_token_history(address: Any, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L482)

Description: Get info about token historical transactions. [Source: Ethplorer]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Token e.g. 0xf3db5fa2c66b7af3eb0c0b782510816cbe4813b8 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in descending order. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | DataFrame with token historical transactions. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_ethplorer_view.display_token_history

```python title='openbb_terminal/decorators.py'
def display_token_history() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L276)

Description: Display info about token history. [Source: Ethplorer]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| address | str | Token balance e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984 | None | False |
| limit | int | Limit of transactions. Maximum 100 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in descending order. | None | False |
| hash_ | bool, | Flag to show transaction hash. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>