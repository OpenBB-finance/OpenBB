---
title: cps
description: A comprehensive guide on how to use the CPS tool for displaying Companies
  per Sectors based on Country and Market Cap. It provides detailed explanation about
  the command-line parameters, their options and usage.
keywords:
- CPS tool
- Companies per Sectors
- Country and Market Cap
- command-line parameters
- max sectors to display
- min percentage to display sector
- output all raw data
- data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/sia/cps - Reference | OpenBB Terminal Docs" />

Companies per Sectors based on Country and Market Cap

### Usage

```python
cps [-M MAX_SECTORS_TO_DISPLAY] [-m MIN_PCT_TO_DISPLAY_SECTOR] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| max_sectors_to_display | Maximum number of sectors to display | 15 | True | None |
| min_pct_to_display_sector | Minimum percentage to display sector | 0.015 | True | None |
| raw | Output all raw data | False | True | None |

![CPS](https://user-images.githubusercontent.com/46355364/153896194-512699a7-ce52-4cbd-869e-89397bc96dc4.png)

---
