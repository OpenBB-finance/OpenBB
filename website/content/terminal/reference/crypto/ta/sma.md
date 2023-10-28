---
title: sma
description: A documentation page elaborating on Simple Moving Averages (sma), their
  application in data smoothing and trend identification. It outlines usage, parameters
  and provides visualized data.
keywords:
- Moving averages
- Data smoothing
- Trend identification
- Simple Moving Average
- Filtering data changes
- sma parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/sma - Reference | OpenBB Terminal Docs" />

Moving Averages are used to smooth the data in an array to help eliminate noise and identify trends. The Simple Moving Average is literally the simplest form of a moving average. Each output value is the average of the previous n values. In a Simple Moving Average, each value in the time period carries equal weight, and values outside of the time period are not included in the average. This makes it less responsive to recent changes in the data, which can be useful for filtering out those changes.

### Usage

```python
sma [-l N_LENGTH] [-o N_OFFSET]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | Window lengths. Multiple values indicated as comma separated values. | 20, 50 | True | None |
| n_offset | offset | 0 | True | range(0, 100) |

![sma](https://user-images.githubusercontent.com/46355364/154311791-5b130d08-55bd-406b-a68e-914a733c5191.png)

---
