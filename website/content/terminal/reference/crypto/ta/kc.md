---
title: kc
description: The documentation provides insights on Keltner Channels (kc), a volatility-based
  band indicating a trend direction. The page explains its usage in Python, various
  parameters like N_LENGTH, N_SCALAR, mamode types (ema, sma, wma, hma, zlma) and
  the N_OFFSET.
keywords:
- kc
- Keltner Channels
- volatility-based bands
- average true range
- ATR
- trend direction
- N_LENGTH
- N_SCALAR
- mamode
- ema
- sma
- wma
- hma
- zlma
- N_OFFSET
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/kc - Reference | OpenBB Terminal Docs" />

Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a trend.The Keltner channel uses the average true range (ATR) or volatility, with breaks above or below the top and bottom barriers signaling a continuation.

### Usage

```python
kc [-l N_LENGTH] [-s N_SCALAR] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window length | 20 | True | range(1, 100) |
| n_scalar | scalar | 2 | True | None |
| s_mamode | mamode | ema | True | ema, sma, wma, hma, zlma |
| n_offset | offset | 0 | True | range(0, 100) |

![kc](https://user-images.githubusercontent.com/46355364/154311120-a769ee53-901b-401f-907f-cacac43ee9b9.png)

---
