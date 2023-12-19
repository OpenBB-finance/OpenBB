---
title: fisher
description: This page provides information about the Fisher Transform, a technical
  indicator that converts prices into a Gaussian normal distribution. The tool helps
  with identifying potential turning points in the price of an asset, and enables
  users to visualize trends and price waves.
keywords:
- Fisher Transform
- technical indicator
- John F. Ehlers
- Gaussian normal distribution
- price turning points
- price trends
- price waves
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/ta/fisher - Reference | OpenBB Terminal Docs" />

The Fisher Transform is a technical indicator created by John F. Ehlers that converts prices into a Gaussian normal distribution.1 The indicator highlights when prices have moved to an extreme, based on recent prices. This may help in spotting turning points in the price of an asset. It also helps show the trend and isolate the price waves within a trend.

### Usage

```python
fisher [-l N_LENGTH]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_length | length | 14 | True | range(1, 100) |

![fisher](https://user-images.githubusercontent.com/46355364/154310853-0abf6cea-71ca-4f07-b009-282c58ab9cfc.png)

---
