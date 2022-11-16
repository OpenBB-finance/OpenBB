---
title: cpexchanges
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cpexchanges

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_coinpaprika_model.get_list_of_exchanges

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_model.py'
def get_list_of_exchanges(symbols: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_model.py#L283)

Description: List exchanges from CoinPaprika API [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbols | str | Comma separated quotes to return e.g quotes=USD,BTC | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascend | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | rank, name, currencies, markets, fiats, confidence_score, reported_volume_24h,
reported_volume_7d ,reported_volume_30d, sessions_per_month, |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_coinpaprika_view.display_all_exchanges

```python title='openbb_terminal/cryptocurrency/overview/coinpaprika_view.py'
def display_all_exchanges(symbol: str, sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/coinpaprika_view.py#L213)

Description: List exchanges from CoinPaprika API. [Source: CoinPaprika]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| currency | str | Quoted currency | None | False |
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