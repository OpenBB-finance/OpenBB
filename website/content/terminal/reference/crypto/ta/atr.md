---
title: atr
description: Averge True Range is used to measure volatility, especially volatility caused by gaps or limit moves
keywords:
- crypto.ta
- atr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto /ta/atr - Reference | OpenBB Terminal Docs" />

Averge True Range is used to measure volatility, especially volatility caused by gaps or limit moves.

### Usage

```python wordwrap
atr [-l N_LENGTH] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| n_length | -l  --length | Window length | 14 | True | None |
| s_mamode | -m  --mamode | mamode | ema | True | ema, sma, wma, hma, zlma |
| n_offset | -o  --offset | offset | 0 | True | None |

---
