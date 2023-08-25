---
title: macd
description: OpenBB Terminal Function
---

# macd

The Moving Average Convergence Divergence (MACD) is the difference between two Exponential Moving Averages. The Signal line is an Exponential Moving Average of the MACD. The MACD signals trend changes and indicates the start of new trend direction. High values indicate overbought conditions, low values indicate oversold conditions. Divergence with the price indicates an end to the current trend, especially if the MACD is at extreme high or low values. When the MACD line crosses above the signal line a buy signal is generated. When the MACD crosses below the signal line a sell signal is generated. To confirm the signal, the MACD should be above zero for a buy, and below zero for a sell.

### Usage

```python
macd [--fast N_FAST] [--slow N_SLOW] [--signal N_SIGNAL]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_fast | The short period. | 12 | True | range(1, 100) |
| n_slow | The long period. | 26 | True | None |
| n_signal | The signal period. | 9 | True | None |

![macd](https://user-images.githubusercontent.com/46355364/154311220-d18eb93e-76b3-4abb-b9c6-86484f462c55.png)

---
