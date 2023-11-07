---
title: rsi
description: This page provides detailed information about the Relative Strength Index
  (RSI), including its calculations, interpretation and usage. It also explains the
  various parameters involved and how to modify them.
keywords:
- RSI
- Relative Strength Index
- overbought
- oversold
- indicator
- price movement
- divergence
- reversal
- parameters
- n_length
- n_scalar
- n_drift
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/rsi - Reference | OpenBB Terminal Docs" />

The Relative Strength Index (RSI) calculates a ratio of the recent upward price movements to the absolute price movement. The RSI ranges from 0 to 100. The RSI is interpreted as an overbought/oversold indicator when the value is over 70/below 30. You can also look for divergence with price. If the price is making new highs/lows, and the RSI is not, it indicates a reversal.

### Usage

```python
rsi [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | None |
| n_scalar | scalar | 100 | True | None |
| n_drift | drift | 1 | True | None |

![rsi](https://user-images.githubusercontent.com/46355364/154311651-99e67e12-1677-43a9-92d9-5998d99fd0db.png)

---
