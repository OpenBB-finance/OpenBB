---
title: stoch
description: Learn about the Stochastic Oscillator, a measurement tool in trading
  ranges. Discover the meaning of overbought and oversold conditions and how to interpret
  the signals from Fast %D and Slow %D. Understand how to use parameters like n_fastkperiod,
  n_slowdperiod, and n_slowkperiod for moving averages.
keywords:
- Stochastic Oscillator
- overbought condition
- oversold condition
- Fast %D
- Slow %D
- buy signal
- sell signal
- Raw %K
- moving average
- n_fastkperiod
- n_slowdperiod
- n_slowkperiod
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/stoch - Reference | OpenBB Terminal Docs" />

The Stochastic Oscillator measures where the close is in relation to the recent trading range. The values range from zero to 100. %D values over 75 indicate an overbought condition; values under 25 indicate an oversold condition. When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses below, it is a sell signal. The Raw %K is generally considered too erratic to use for crossover signals.

### Usage

```python
stoch [-k N_FASTKPERIOD] [-d N_SLOWDPERIOD] [--slowkperiod N_SLOWKPERIOD]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_fastkperiod | The time period of the fastk moving average | 14 | True | range(1, 100) |
| n_slowdperiod | The time period of the slowd moving average | 3 | True | range(1, 100) |
| n_slowkperiod | The time period of the slowk moving average | 3 | True | range(1, 100) |

![stoch](https://user-images.githubusercontent.com/46355364/154311913-d58e58bb-d116-44dd-ae4b-44e59c25f22a.png)

---
