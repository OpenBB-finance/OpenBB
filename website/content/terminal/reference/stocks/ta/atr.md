---
title: atr
description: Technical documentation of the 'atr' function or Average True Range used
  for measuring volatility in financial markets, particularly those arising due to
  gaps or limit moves. The page highlights how to use the function using Python, its
  parameters, and different modes.
keywords:
- Averge True Range
- atr
- volatility measurement
- trading algorithms
- financial markets
- technical analysis
- ema
- sma
- wma
- hma
- zlma
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/atr - Reference | OpenBB Terminal Docs" />

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
