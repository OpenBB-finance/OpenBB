---
title: events
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# events

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinpaprika_model.get_coin_events_by_id

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py'
def get_coin_events_by_id(symbol: str, sortby: Any, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L90)

Description: Get all events related to given coin like conferences, start date of futures trading etc.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum' | None | False |
| sortby | str | Key by which to sort data. Every column name is valid
(see for possible values:
https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get). | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Events found for given coin
Columns: id, date , date_to, name, description, is_conference, link, proof_image_link |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinpaprika_view.display_events

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py'
def display_events(symbol: str, limit: int, sortby: str, ascend: bool, links: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L137)

Description: Get all events for given coin id. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data. Every column name is valid
(see for possible values:
https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1events/get). | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| links | bool | Flag to display urls | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>