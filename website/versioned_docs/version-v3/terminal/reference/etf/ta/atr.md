---
title: atr
description: OpenBB Terminal Function
---

# atr

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
