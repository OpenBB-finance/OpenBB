---
title: zlma
description: The ZLEMA (Zero Lag Exponential Moving Average) is a technical indicator
  developed by John Ehlers and Ric Way. This documentation page explains how to use
  it, focusing on implementation with Python and specifying its parameters including
  window lengths (N_LENGTH) and offset (N_OFFSET).
keywords:
- ZLEMA
- exponential moving average
- de-lagged data
- EMA
- zero lag exponential moving average
- John Ehlers
- Ric Way
- zlma
- N_LENGTH
- N_OFFSET
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/zlma - Reference | OpenBB Terminal Docs" />

The zero lag exponential moving average (ZLEMA) indicator was created by John Ehlers and Ric Way. The idea is do a regular exponential moving average (EMA) calculation but on a de-lagged data instead of doing it on the regular data. Data is de-lagged by removing the data from "lag" days ago thus removing (or attempting to) the cumulative effect of the moving average.

### Usage

```python
zlma [-l N_LENGTH] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window lengths. Multiple values indicated as comma separated values. | 20 | True | None |
| n_offset | offset | 0 | True | range(0, 100) |

![zlma](https://user-images.githubusercontent.com/46355364/154312786-bc60268b-9da9-4fd9-bed6-fc95f5560075.png)

---
