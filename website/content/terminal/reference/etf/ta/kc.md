---
title: kc
description: This documentation page provides detailed information about Keltner Channels,
  a volatility-based band applied onto an asset's price. These channels aid in trend
  determination by employing average true range (ATR) or volatility. The page also
  provides comprehensive instructions about how to use and parameterize the 'kc' tool.
keywords:
- Keltner Channels
- volatility-based bands
- average true range
- ATR
- trend determination
- kc
- kc parameters
- n_length
- n_scalar
- s_mamode
- n_offset
- kc usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/kc - Reference | OpenBB Terminal Docs" />

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
