---
title: chains_yf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# chains_yf

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_yfinance_model.get_option_chain

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_option_chain(symbol: str, expiry: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L158)

Description: Gets option chain from yf for given ticker and expiration

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get options for | None | False |
| expiry | str | Date to get options for. YYYY-MM-DD | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| yf.ticker.Options | Options chain |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_yfinance_view.display_chains

```python title='openbb_terminal/stocks/options/yfinance_view.py'
def display_chains(symbol: str, expiry: str, min_sp: float, max_sp: float, calls_only: bool, puts_only: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_view.py#L72)

Description: Display option chains for given ticker and expiration

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| expiry | str | Expiration for option chain | None | False |
| min_sp | float | Min strike | None | False |
| max_sp | float | Max strike | None | False |
| calls_only | bool | Flag to get calls only | None | False |
| puts_only | bool | Flag to get puts only | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>