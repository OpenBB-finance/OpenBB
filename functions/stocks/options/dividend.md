---
title: dividend
description: OpenBB SDK Function
---

# dividend

## stocks_options_yfinance_model.get_dividend

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def get_dividend(symbol: str) -> Series:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L185)

Description: Gets option chain from yf for given ticker and expiration

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get options for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| yf.ticker.Dividends | Dividends |

## Examples

