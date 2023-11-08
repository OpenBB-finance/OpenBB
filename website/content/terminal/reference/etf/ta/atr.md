---
title: atr
description: This page provides comprehensive information about the Average True Range
  (ATR) including its usage, implementation, and parameters. It serves as a key resource
  for understanding ATR, a widely used tool for measuring volatility in market prices.
keywords:
- average true range
- volatility measure
- ATR usage
- ATR parameters
- ema
- sma
- wma
- hma
- zlma
- n_length
- s_mamode
- n_offset
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/atr - Reference | OpenBB Terminal Docs" />

Averge True Range is used to measure volatility, especially volatility caused by gaps or limit moves.

### Usage

```python
atr [-l N_LENGTH] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window length | 14 | True | None |
| s_mamode | mamode | ema | True | ema, sma, wma, hma, zlma |
| n_offset | offset | 0 | True | None |

---
