---
title: tv
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# tv

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_bitquery_model.get_token_volume_on_dexes

```python title='openbb_terminal/cryptocurrency/onchain/bitquery_model.py'
def get_token_volume_on_dexes(symbol: str, trade_amount_currency: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L513)

Description: Get token volume on different Decentralized Exchanges. [Source: https://graphql.bitquery.io/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ERC20 token symbol. | None | False |
| trade_amount_currency | str | Currency to display trade amount in. | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Token volume on Decentralized Exchanges |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_bitquery_view.display_dex_volume_for_token

```python title='openbb_terminal/decorators.py'
def display_dex_volume_for_token() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L160)

Description: Display token volume on different Decentralized Exchanges.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ERC20 token symbol or address | None | False |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Token volume on different decentralized exchanges |

## Examples



</TabItem>
</Tabs>