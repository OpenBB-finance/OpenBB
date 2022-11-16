---
title: cmctop
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cmctop

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_disc_coinmarketcap_model.get_cmc_top_n

```python title='openbb_terminal/decorators.py'
def get_cmc_top_n() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L27)

Description: Shows top n coins. [Source: CoinMarketCap]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to
Coin Market Cap:s API documentation, see:
https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest | None | False |
| ascend | bool | Whether to sort ascending or descending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top coin on CoinMarketCap |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_disc_coinmarketcap_view.display_cmc_top_coins

```python title='openbb_terminal/decorators.py'
def display_cmc_top_coins() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L17)

Description: Shows top n coins. [Source: CoinMarketCap]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| sortby | str | Key to sort data. The table can be sorted by every of its columns. Refer to
Coin Market Cap:s API documentation, see:
https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>