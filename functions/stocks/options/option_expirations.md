---
title: option_expirations
description: OpenBB SDK Function
---

# option_expirations

## stocks_options_yfinance_model.option_expirations

```python title='openbb_terminal/stocks/options/yfinance_model.py'
def option_expirations(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/yfinance_model.py#L137)

Description: Get available expiration dates for given ticker

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get expirations for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| List[str] | List of of available expirations |

## Examples

