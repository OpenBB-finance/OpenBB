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

<HeadTitle title="portfolio/mret - Reference | OpenBB Terminal Docs" />

Monthly returns

### Usage

```python
mret [-p PERIOD] [-s]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| period | Period to select start end of the year returns | all | True | 3y, 5y, 10y, all |
| show_vals | Show monthly returns on heatmap | False | True | None |

---
