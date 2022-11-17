---
title: cbpairs
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cbpairs

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_coinbase_model.get_trading_pairs

```python title='openbb_terminal/cryptocurrency/overview/coinbase_model.py'
def get_trading_pairs(limit: int, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinbase_model.py#L24)

Description: Get a list of available currency pairs for trading. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Top n of pairs | None | False |
| sortby | str | Key to sortby data | None | False |
| ascend | bool | Sort descending flag | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Available trading pairs on Coinbase |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_coinbase_view.display_trading_pairs

```python title='openbb_terminal/decorators.py'
def display_trading_pairs() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L19)

Description: Displays a list of available currency pairs for trading. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Top n of pairs | None | False |
| sortby | str | Key to sortby data | None | False |
| ascend | bool | Sort ascending flag | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>