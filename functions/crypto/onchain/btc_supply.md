---
title: btc_supply
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# btc_supply

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_onchain_blockchain_model.get_btc_circulating_supply

```python title='openbb_terminal/cryptocurrency/onchain/blockchain_model.py'
def get_btc_circulating_supply() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_model.py#L42)

Description: Returns BTC circulating supply [Source: https://api.blockchain.info/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | BTC circulating supply |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_onchain_blockchain_view.display_btc_circulating_supply

```python title='openbb_terminal/cryptocurrency/onchain/blockchain_view.py'
def display_btc_circulating_supply(start_date: str, end_date: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/onchain/blockchain_view.py#L28)

Description: Returns BTC circulating supply [Source: https://api.blockchain.info/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | None | False |
| end_date | str | Final date, format YYYY-MM-DD | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>