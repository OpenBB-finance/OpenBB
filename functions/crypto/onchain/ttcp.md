---
title: ttcp
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ttcp

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_bitquery_model.get_most_traded_pairs

```python title='openbb_terminal/cryptocurrency/onchain/bitquery_model.py'
def get_most_traded_pairs(network: str, exchange: str, limit: int, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L658)

Description: Get most traded crypto pairs on given decentralized exchange in chosen time period.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| network | str | EVM network. One from list: bsc (binance smart chain), ethereum or matic | None | False |
| exchange |  | Decentralized exchange name | None | False |
| limit |  | Number of days taken into calculation account. | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_bitquery_view.display_most_traded_pairs

```python title='openbb_terminal/decorators.py'
def display_most_traded_pairs() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L284)

Description: Display most traded crypto pairs on given decentralized exchange in chosen time period.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| exchange |  | Decentralized exchange name | None | False |
| days |  | Number of days taken into calculation account. | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most traded crypto pairs on given decentralized exchange in chosen time period. |

## Examples



</TabItem>
</Tabs>