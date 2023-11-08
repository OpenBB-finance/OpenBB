---
title: kc
description: In-depth explanation and usage of the KC function for Keltner Channels;
  including parameters, and how to utilize it to determine trend direction through
  volatility-based bands.
keywords:
- Keltner Channels
- volatility-based bands
- asset's price
- average true range
- ATR
- volatility
- trend direction
- kc
- n_length
- n_scalar
- s_mamode
- n_offset
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/kc - Reference | OpenBB Terminal Docs" />

Keltner Channels are volatility-based bands that are placed on either side of an asset's price and can aid in determining the direction of a trend.The Keltner channel uses the average true range (ATR) or volatility, with breaks above or below the top and bottom barriers signaling a continuation.

### Usage

```python
kc [-l N_LENGTH] [-s N_SCALAR] [-m {ema,sma,wma,hma,zlma}] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window length | 20 | True | None |
| n_scalar | scalar | 2 | True | None |
| s_mamode | mamode | ema | True | ema, sma, wma, hma, zlma |
| n_offset | offset | 0 | True | None |

![kc](https://user-images.githubusercontent.com/46355364/154311120-a769ee53-901b-401f-907f-cacac43ee9b9.png)

---
