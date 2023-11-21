---
title: mret
description: This page is about the mret tool that helps to calculate monthly returns.
  It contains information about its usage, parameters, and various options.
keywords:
- mret
- monthly returns
- heatmap
- parameters
- usage
- periods
- choices
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /mret - Reference | OpenBB Terminal Docs" />

Monthly returns

### Usage

```python wordwrap
mret [-p PERIOD] [-i {both,portfolio,benchmark}] [-g] [-s]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| period | -p  --period | Period to select start end of the year returns | all | True | 3y, 5y, 10y, all |
| instrument | -i  --instrument | Whether to show portfolio or benchmark monthly returns. By default both are shown in one table. | both | True | both, portfolio, benchmark |
| graph | -g  --graph | Plot the monthly returns on a heatmap | False | True | None |
| show_vals | -s  --show | Show monthly returns on heatmap | False | True | None |

---
