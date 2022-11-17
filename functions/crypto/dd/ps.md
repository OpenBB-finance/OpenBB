---
title: ps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ps

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinpaprika_model.get_tickers_info_for_coin

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py'
def get_tickers_info_for_coin(symbol: str, quotes: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L296)

Description: Get all most important ticker related information for given coin id [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Id of coin from CoinPaprika | None | False |
| quotes | str | Comma separated quotes to return e.g quotes = USD, BTC | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Most important ticker related information
Columns: Metric, Value |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinpaprika_view.display_price_supply

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py'
def display_price_supply(from_symbol: str, to_symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L304)

Description: Get ticker information for single coin [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol (e.g. BTC) | None | False |
| to_symbol | str | Quoted currency | None | False |
| export | str | Export dataframe data to csv,json,xlsx | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>