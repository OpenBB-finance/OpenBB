---
title: vsurf
description: Learn the usage of vsurf, a Python tool for plotting a 3D volatility
  surface. Understand the parameters and see a sample representation.
keywords:
- vsurf
- 3D volatility surface
- IV
- OI
- LP
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/vsurf - Reference | OpenBB Terminal Docs" />

Plot 3D volatility surface.

### Usage

```python
vsurf [-z {IV,OI,LP}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| z | The data for the Z axis | IV | True | IV, OI, LP |

![vsurf](https://user-images.githubusercontent.com/46355364/154290744-1e427337-1a9a-4b84-a85a-9f07571882ba.png)

---
