---
title: load
description: This page provides information about the 'load' feature designed to retrieve
  historical data. It details the usage and various parameters with their functions.
keywords:
- historical data
- load function
- fund search
- date range
- parameters
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="funds /load - Reference | OpenBB Terminal Docs" />

Load the fund to perform analysis on.

### Usage

```python wordwrap
load --fund FUND [-s START] [-e END]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| fund | --fund | Fund string to search for | None | False | None |
| start | -s  --start | The starting date (format YYYY-MM-DD) of the stock | 2022-11-21 | True | None |
| end | -e  --end | The ending date (format YYYY-MM-DD) of the stock | 2023-11-21 | True | None |

---
