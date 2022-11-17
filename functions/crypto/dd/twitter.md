---
title: twitter
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# twitter

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinpaprika_model.get_coin_twitter_timeline

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py'
def get_coin_twitter_timeline(symbol: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_model.py#L42)

Description: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | id of coin from coinpaprika e.g. Ethereum - > 'eth-ethereum' | None | False |
| sortby | str | Key by which to sort data. Every column name is valid
(see for possible values:
https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get). | None | False |
| ascend | bool | Flag to sort data descending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Twitter timeline for given coin.
Columns: date, user_name, status, retweet_count, like_count |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinpaprika_view.display_twitter

```python title='openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py'
def display_twitter(symbol: str, limit: int, sortby: str, ascend: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinpaprika_view.py#L87)

Description: Get twitter timeline for given coin id. Not more than last 50 tweets [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency symbol (e.g. BTC) | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data. Every column name is valid
(see for possible values:
https://api.coinpaprika.com/docs#tag/Coins/paths/~1coins~1%7Bcoin_id%7D~1twitter/get). | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>