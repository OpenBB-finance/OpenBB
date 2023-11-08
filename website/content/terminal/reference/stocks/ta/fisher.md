---
title: fisher
description: The page provides a comprehensive guide to the Fisher Transform, a technical
  indicator by John F. Ehlers. It helps in highlighting extreme prices based on recent
  values, identifying turning points, showing the trend and isolating price waves.
  The functions, usage and parameters of the Fisher Transform are elaborately discussed.
keywords:
- Fisher Transform
- technical indicator
- John F. Ehlers
- Gaussian normal distribution
- extreme prices
- turning points
- price of an asset
- trend indication
- price waves
- Fisher usage
- Fisher parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/ta/fisher - Reference | OpenBB Terminal Docs" />

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
