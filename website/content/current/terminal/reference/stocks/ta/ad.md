---
title: ad
description: An in-depth explanation of Accumulation/Distribution Line (AD), its interpretation,
  and usage. The page also provides a Python script for the indicator and describes
  its parameters.
keywords:
- Accumulation/Distribution Line (AD)
- AD Indicator
- Close Location Value
- CLV
- Stock Market Indicator
- Python Script
- b_use_open
- On Balance Volume (OBV)
- Volume Times
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/ad - Reference | OpenBB Terminal Docs" />

The Accumulation/Distribution Line is similar to the On Balance Volume (OBV), which sums the volume times +1/-1 based on whether the close is higher than the previous close. The Accumulation/Distribution indicator, however multiplies the volume by the close location value (CLV). The CLV is based on the movement of the issue within a single bar and can be +1, -1 or zero. The Accumulation/Distribution Line is interpreted by looking for a divergence in the direction of the indicator relative to price. If the Accumulation/Distribution Line is trending upward it indicates that the price may follow. Also, if the Accumulation/Distribution Line becomes flat while the price is still rising (or falling) then it signals an impending flattening of the price.

### Usage

```python
ad [--open]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| b_use_open | uses open value of stock | False | True | None |

![ad](https://user-images.githubusercontent.com/46355364/154309283-9512c6c0-dda3-4348-9350-105238676479.png)

---
