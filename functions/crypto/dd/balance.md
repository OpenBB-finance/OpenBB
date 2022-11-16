---
title: balance
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# balance

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_binance_model.get_balance

```python title='openbb_terminal/decorators.py'
def get_balance() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L175)

Description: Get account holdings for asset. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency | None | False |
| to_symbol | str | Cryptocurrency | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with account holdings for an asset |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_binance_view.display_balance

```python title='openbb_terminal/cryptocurrency/due_diligence/binance_view.py'
def display_balance(from_symbol: str, to_symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_view.py#L64)

Description: Get account holdings for asset. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency | None | False |
| to_symbol | str | Cryptocurrency | None | False |
| export | str | Export dataframe data to csv,json,xlsx | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>