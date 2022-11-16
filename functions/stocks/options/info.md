---
title: info
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# info

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_yfinance_model.get_info

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_info(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L279)

Description: Get info for a given ticker

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | The ticker symbol to get the price for | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| price | float | The info for a given ticker | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_barchart_view.print_options_data

```python title='openbb_terminal/stocks/options/barchart_view.py'
def print_options_data(symbol: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/barchart_view.py#L15)

Description: Scrapes Barchart.com for the options information

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get options info for | None | False |
| export | str | Format of export file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>