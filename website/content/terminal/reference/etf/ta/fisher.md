---
title: fisher
description: A technical documentation page highlighting the Fisher Transform, a technical
  indicator, its usage, parameters, and purpose in identifying price turning points
  and trends.
keywords:
- Fisher Transform
- Technical Indicator
- John F. Ehlers
- Price Turning Points
- Price Trends
- Gaussian Normal Distribution
- Isolate Price Waves
- Parameter Configuration
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf/ta/fisher - Reference | OpenBB Terminal Docs" />

The Fisher Transform is a technical indicator created by John F. Ehlers that converts prices into a Gaussian normal distribution.1 The indicator highlights when prices have moved to an extreme, based on recent prices. This may help in spotting turning points in the price of an asset. It also helps show the trend and isolate the price waves within a trend.

### Usage

```python
fisher [-l N_LENGTH]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | None |

![fisher](https://user-images.githubusercontent.com/46355364/154310853-0abf6cea-71ca-4f07-b009-282c58ab9cfc.png)

---
