---
title: wfpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# wfpe

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_withdrawalfees_model.get_crypto_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py'
def get_crypto_withdrawal_fees(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L209)

Description: Scrapes coin withdrawal fees per exchange

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to check withdrawal fees. By default bitcoin | bitcoin | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | - str:              Overall statistics (exchanges, lowest, average and median)
- pandas.DataFrame: Exchange, Withdrawal Fee, Minimum Withdrawal Amount |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_withdrawalfees_view.display_crypto_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py'
def display_crypto_withdrawal_fees(symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L86)

Description: Coin withdrawal fees per exchange

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Coin to check withdrawal fees | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>