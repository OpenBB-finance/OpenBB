---
title: c
description: Command for retrieving a detailed candlestick chart for the specified
  cryptocurrency coin. This includes an opening and closing price, as well as the
  high and low within a definite time interval. Options to include support/resistant
  lines and Fibonacci retracement levels are available.
keywords:
- Crypto Currency
- Crypto Coin
- Candlestick Chart
- Crypto Exchange
- Trading Parameters
- Support Resistance Lines
- Fibonacci Retracement Levels
- Crypto Symbol
- Crypto Trading Command
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="charts: c - Telegram Reference | OpenBB Bot Docs" />

This command will retrieve a candlestick chart for the crypto coin provided. The interval provided must be a valid time interval (default 15 minutes). The chart will be displayed to the user and will contain information such as the opening and closing prices, the high and low, the volume, and any other relevant information.

### Usage

```python wordwrap
/c symbol [currency] [exchange] [interval] [srlines] [fibs]
```

---

## Parameters

| Name | Description | Optional | Choices |
| ---- | ----------- | -------- | ------- |
| symbol | Crypto Symbol | False | None |
| currency | Crypto Currency. Default: USDT | True | None |
| exchange | Crypto Exchange. Default: binanceus | True | None |
| interval | 1m: 1 Minute 3m: 3 Minutes 5m: 5 Minutes 15m: 15 Minutes 30m: 30 Minutes 1hr: 1 Hour 1d: 1 Day 1wk: 1 Week 1mo: 1 Month | True | 1m, 3m, 5m, 15m, 30m, 1hr, 1d, 1wk, 1mo |
| srlines | Show Support/Resistance Lines. Default: False | True | None |
| fibs | Show Fibonacci Retracement Levels. Default: False | True | None |


---

## Examples

```
/c doge
```

```
/c doge interval:3m
```
---
