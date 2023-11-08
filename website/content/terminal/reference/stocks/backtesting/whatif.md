---
title: whatif
description: Learn about the 'whatif' command line tool which provides a hypothetical
  scenario of having bought a certain number of shares on a specific date. This tool
  can be used for backward investment analysis and scenario planning.
keywords:
- whatif
- shares
- share trading
- investment scenario
- investment analysis
- command line tool
- DATE_SHARES_ACQUIRED
- NUM_SHARES_ACQUIRED
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/backtesting/whatif - Reference | OpenBB Terminal Docs" />

Displays what if scenario of having bought X shares at date Y

### Usage

```python
whatif [-d DATE_SHARES_ACQUIRED] [-n NUM_SHARES_ACQUIRED]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| date_shares_acquired | Date at which the shares were acquired | None | True | None |
| num_shares_acquired | Number of shares acquired | 1.0 | True | None |

---
