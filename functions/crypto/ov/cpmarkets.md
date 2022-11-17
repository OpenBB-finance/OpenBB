---
title: cpmarkets
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpmarkets

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_coinpaprika_model.get_coins_market_info

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_model.py'
def get_coins_market_info(symbols: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L241)

Description: Returns basic coin information for all coins from CoinPaprika API [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated quotes to return e.g quotes=USD,BTC | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascend | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | rank, name, symbol, price, volume_24h, mcap_change_24h,
pct_change_1h, pct_change_24h, ath_price, pct_from_ath, |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_coinpaprika_view.display_all_coins_market_info

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_view.py'
def display_all_coins_market_info(symbol: str, sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L105)

Description: Displays basic market information for all coins from CoinPaprika API. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Quoted currency | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| links | bool | Flag to display urls | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>