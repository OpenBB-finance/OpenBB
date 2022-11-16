---
title: top
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# top

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_ethplorer_model.get_top_tokens

```python title='openbb_terminal/cryptocurrency/onchain/ethplorer_model.py'
def get_top_tokens(sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/ethplorer_model.py#L268)

Description: Get top 50 tokens. [Source: Ethplorer]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
|  | DataFrame with list of top 50 tokens. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_ethplorer_view.display_top_tokens

```python title='openbb_terminal/decorators.py'
def display_top_tokens() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L70)

Description: Display top ERC20 tokens [Source: Ethplorer]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Limit of transactions. Maximum 100 | None | False |
| sortby | str | Key to sort by. | None | False |
| ascend | str | Sort in descending order. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>