---
title: stoch
description: OpenBB Terminal Function
---

# stoch

The Stochastic Oscillator measures where the close is in relation to the recent trading range. The values range from zero to 100. %D values over 75 indicate an overbought condition; values under 25 indicate an oversold condition. When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses below, it is a sell signal. The Raw %K is generally considered too erratic to use for crossover signals.

### Usage

```python
usage: stoch [-k N_FASTKPERIOD] [-d N_SLOWDPERIOD] [--slowkperiod N_SLOWKPERIOD]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_fastkperiod | The time period of the fastk moving average | 14 | True | range(1, 100) |
| n_slowdperiod | The time period of the slowd moving average | 3 | True | range(1, 100) |
| n_slowkperiod | The time period of the slowk moving average | 3 | True | range(1, 100) |
---

