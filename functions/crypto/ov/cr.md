---
title: cr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cr

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_loanscan_model.get_rates

```python title='openbb_terminal/cryptocurrency/overview/loanscan_model.py'
def get_rates(rate_type: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/loanscan_model.py#L267)

Description: Returns crypto {borrow,supply} interest rates for cryptocurrencies across several platforms

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| rate_type | str | Interest rate type: {borrow, supply}. Default: supply | supply | False |

## Returns

| Type | Description |
| ---- | ----------- |
| crypto interest rates per platform | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_loanscan_view.display_crypto_rates

```python title='openbb_terminal/cryptocurrency/overview/loanscan_view.py'
def display_crypto_rates(symbols: str, platforms: str, rate_type: str, limit: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/loanscan_view.py#L24)

Description: Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| rate_type | str | Interest rate type: {borrow, supply}. Default: supply | supply | False |
| symbols | str | Crypto separated by commas. Default: BTC,ETH,USDT,USDC | BTC | False |
| platforms | str | Platforms separated by commas. Default: BlockFi,Ledn,SwissBorg,Youhodler | BlockFi | False |
| limit | int | Number of records to show | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>