---
title: mkt
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mkt

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinpaprika_model.get_coin_markets_by_id

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py'
def get_coin_markets_by_id(symbol: str, quotes: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L187)

Description: All markets for given coin and currency [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin Parpika identifier of coin e.g. eth-ethereum | None | False |
| quotes | str | Comma separated list of quotes to return.
Example: quotes=USD,BTC
Allowed values:
BTC, ETH, USD, EUR, PLN, KRW, GBP, CAD, JPY, RUB, TRY, NZD, AUD, CHF, UAH, HKD, SGD, NGN,
PHP, MXN, BRL, THB, CLP, CNY, CZK, DKK, HUF, IDR, ILS, INR, MYR, NOK, PKR, SEK, TWD, ZAR,
VND, BOB, COP, PEN, ARS, ISK | None | False |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:
https://api.coinpaprika.com/v1). | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | All markets for given coin and currency |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinpaprika_view.display_markets

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py'
def display_markets(from_symbol: str, to_symbol: str, limit: int, sortby: str, ascend: bool, links: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L242)

Description: Get all markets for given coin id. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol (e.g. BTC) | None | False |
| to_symbol | str | Quoted currency | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data. Every column name is valid (see for possible values:
https://api.coinpaprika.com/v1). | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| links | bool | Flag to display urls | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>