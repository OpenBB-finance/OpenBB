---
title: bbands
description: Documentation for Bollinger Bands (bbands), an indicator of overbought
  or oversold conditions in market prices. Includes details on how to use and interpret
  bbands, as well as information on bbands' parameters (such as n_length, n_std, and
  s_mamode).
keywords:
- Bollinger Bands
- overbought conditions
- oversold conditions
- volatility
- price target
- support level
- resistance level
- bbands
- n_length
- n_std
- s_mamode
- sma
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/bbands - Reference | OpenBB Terminal Docs" />

Bollinger Bands consist of three lines. The middle band is a simple moving average (generally 20 periods) of the typical price (TP). The upper and lower bands are F standard deviations (generally 2) above and below the middle band. The bands widen and narrow when the volatility of the price is higher or lower, respectively. Bollinger Bands do not, in themselves, generate buy or sell signals; they are an indicator of overbought or oversold conditions. When the price is near the upper or lower band it indicates that a reversal may be imminent. The middle band becomes a support or resistance level. The upper and lower bands can also be interpreted as price targets. When the price bounces off of the lower band and crosses the middle band, then the upper band becomes the price target.

### Usage

```python
bbands [-l N_LENGTH] [-s N_STD] [-m S_MAMODE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 15 | True | None |
| n_std | std | 2 | True | None |
| s_mamode | mamode | sma | True | None |

![bbands](https://user-images.githubusercontent.com/46355364/154309951-116f3c31-342d-4ceb-b489-8b0ba78eb3a0.png)

---
