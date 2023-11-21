---
title: gh
description: Learn how to utilize the GH command line tool to track GitHub activity
  for a given crypto coin. Discover how to filter by development activity, set frequency
  intervals, and define start and end dates with this powerful Python-based
  tool.
keywords:
- Github activity
- Pull Request
- Issue
- command line tool
- development activity
- frequency intervals
- start and end dates
- Santiment
- tracking tool
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="crypto/dd/gh - Reference | OpenBB Terminal Docs" />

Display github activity over time for a given coin. Github activity includes the following actions: creating a Pull Request, an Issue, commenting on an issue / PR, and many more. See detailed definition at https://academy.santiment.net/metrics/development-activity/ [Source: https://santiment.net/]

### Usage

```python
gh [-i INTERVAL] [-d DEV] [-s START] [-end END]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| interval | Frequency interval. Default: 1d | 1d | True | None |
| dev | Filter only for development activity. Default: False | False | True | None |
| start | Initial date. Default: A year ago | 2021-11-25 | True | None |
| end | End date. Default: Today | 2022-11-25 | True | None |

---
