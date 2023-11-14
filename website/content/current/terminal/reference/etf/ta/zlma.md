---
title: zlma
description: Zero lag exponential moving average (ZLEMA) indicator documentation.
  Learn how to use and implement the ZLEMA in your data studies with its parameters
  and usage. Devised by John Ehlers and Ric Way, ZLEMA aids in providing a de-lagged
  calculation of data.
keywords:
- zlma
- zero lag exponential moving average
- John Ehlers
- Ric Way
- EMA
- de-lagged data
- moving average
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/zlma - Reference | OpenBB Terminal Docs" />

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
| n_offset | offset | 0 | True | None |

![zlma](https://user-images.githubusercontent.com/46355364/154312786-bc60268b-9da9-4fd9-bed6-fc95f5560075.png)

---
