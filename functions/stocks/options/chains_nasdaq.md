---
title: chains_nasdaq
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# chains_nasdaq

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_nasdaq_model.get_chain_given_expiration

```python title='openbb_terminal/stocks/options/nasdaq_model.py'
def get_chain_given_expiration(symbol: str, expiration: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/nasdaq_model.py#L113)

Description: Get option chain for symbol at a given expiration

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get chain for | None | False |
| expiration | None | Expiration to get chain for | None | None |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of option chain |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_nasdaq_view.display_chains

```python title='openbb_terminal/stocks/options/nasdaq_view.py'
def display_chains(symbol: str, expiry: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/nasdaq_view.py#L313)

Description: Display option chain for given expiration

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| expiry | str | Expiry date for options | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>