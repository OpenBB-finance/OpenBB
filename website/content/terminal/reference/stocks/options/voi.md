---
title: voi
description: The voi page provides a guide on how to plot Volume + Open Interest of
  calls vs puts with parameters like minimum volume, minimum strike price and maximum
  strike price. It's an integral part of a python-based toolkit.
keywords:
- voi
- Volume
- Open Interest
- strike price
- plot
- minimum volume
- maximum strike price
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/options/voi - Reference | OpenBB Terminal Docs" />

Plots Volume + Open Interest of calls vs puts.

### Usage

```python
voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| min_vol | minimum volume (considering open interest) threshold of the plot. | -1 | True | None |
| min_sp | minimum strike price to consider in the plot. | -1 | True | None |
| max_sp | maximum strike price to consider in the plot. | -1 | True | None |

![voi](https://user-images.githubusercontent.com/46355364/154290408-ae5d50ff-74ea-4705-b8ea-e4eebc842bb6.png)

---
