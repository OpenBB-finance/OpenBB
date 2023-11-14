---
title: ema
description: This is an explanation and usage guideline for the Exponential Moving
  Average (EMA), a core tool in technical analysis. Learn about its distinction from
  the Simple Moving Average and understand how it places greater contribution on recent
  values, making it more responsive to changes in data.
keywords:
- Exponential Moving Average
- technical analysis
- Simple Moving Average
- ema
- ema parameters
- ema usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/ema - Reference | OpenBB Terminal Docs" />

The Exponential Moving Average is a staple of technical analysis and is used in countless technical indicators. In a Simple Moving Average, each value in the time period carries equal weight, and values outside of the time period are not included in the average. However, the Exponential Moving Average is a cumulative calculation, including all data. Past values have a diminishing contribution to the average, while more recent values have a greater contribution. This method allows the moving average to be more responsive to changes in the data.

### Usage

```python
ema [-l N_LENGTH] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window lengths. Multiple values indicated as comma separated values. | 20, 50 | True | None |
| n_offset | offset | 0 | True | None |

![ema](https://user-images.githubusercontent.com/46355364/154310578-6f4a51a8-3667-497c-9c50-7ff16e256fb6.png)

---
