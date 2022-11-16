---
title: lt
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# lt

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_bitquery_model.get_dex_trades_by_exchange

```python title='openbb_terminal/cryptocurrency/onchain/bitquery_model.py'
def get_dex_trades_by_exchange(trade_amount_currency: str, limit: int, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/bitquery_model.py#L266)

Description: Get trades on Decentralized Exchanges aggregated by DEX [Source: https://graphql.bitquery.io/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | False |
| limit | int | Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
on server side) | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trades on Decentralized Exchanges aggregated by DEX |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_bitquery_view.display_dex_trades

```python title='openbb_terminal/decorators.py'
def display_dex_trades() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L22)

Description: Trades on Decentralized Exchanges aggregated by DEX or Month

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| kind | str | Aggregate trades by dex or time | None | False |
| trade_amount_currency | str | Currency of displayed trade amount. Default: USD | USD | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| days | int | Last n days to query data. Maximum 365 (bigger numbers can cause timeouts
on server side) | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>