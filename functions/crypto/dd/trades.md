---
title: trades
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# trades

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinbase_model.get_trades

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py'
def get_trades(symbol: str, limit: int, side: Optional[Any]) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L101)

Description: Get last N trades for chosen trading pair. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| limit | int | Last `limit` of trades. Maximum is 1000. | None | False |
| side | str | You can chose either sell or buy side. If side is not set then all trades will be displayed. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Last N trades for chosen trading pairs. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinbase_view.display_trades

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py'
def display_trades(symbol: str, limit: int, side: Optional[str], export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py#L51)

Description: Display last N trades for chosen trading pair. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| limit | int | Last <limit> of trades. Maximum is 1000. | None | False |
| side | Optional[str] | You can chose either sell or buy side. If side is not set then all trades will be displayed. | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>