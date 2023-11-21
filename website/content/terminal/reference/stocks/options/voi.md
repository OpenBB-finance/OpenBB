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

<HeadTitle title="stocks /options/voi - Reference | OpenBB Terminal Docs" />

Plots Volume + Open Interest of calls vs puts.

### Usage

```python wordwrap
voi [-v MIN_VOL] [-m MIN_SP] [-M MAX_SP] [-e {2023-11-24,2023-12-01,2023-12-08,2023-12-15,2023-12-22,2023-12-29,2024-01-19,2024-02-16,2024-03-15,2024-04-19,2024-06-21,2024-07-19,2024-09-20,2024-12-20,2025-01-17,2025-06-20,2025-09-19,2025-12-19,2026-01-16,}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| min_vol | -v  --minv | minimum volume (considering open interest) threshold of the plot. | -1 | True | None |
| min_sp | -m  --min | minimum strike price to consider in the plot. | -1 | True | None |
| max_sp | -M  --max | maximum strike price to consider in the plot. | -1 | True | None |
| exp | -e  --expiration | Select expiration date (YYYY-MM-DD) |  | True | 2023-11-24, 2023-12-01, 2023-12-08, 2023-12-15, 2023-12-22, 2023-12-29, 2024-01-19, 2024-02-16, 2024-03-15, 2024-04-19, 2024-06-21, 2024-07-19, 2024-09-20, 2024-12-20, 2025-01-17, 2025-06-20, 2025-09-19, 2025-12-19, 2026-01-16,  |

![voi](https://user-images.githubusercontent.com/46355364/154290408-ae5d50ff-74ea-4705-b8ea-e4eebc842bb6.png)

---
