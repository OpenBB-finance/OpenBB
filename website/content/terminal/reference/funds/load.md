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

Get historical data.

### Usage

```python
load --fund FUND [FUND ...] [-n] [-s START] [-e END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| fund | Fund string to search for | None | False | None |
| name | Flag to indicate name provided instead of symbol. | False | True | None |
| start | The starting date (format YYYY-MM-DD) of the fund | 2021-11-24 | True | None |
| end | The ending date (format YYYY-MM-DD) of the fund | 2022-11-25 | True | None |

---
