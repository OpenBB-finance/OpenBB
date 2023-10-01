---
title: gh
description: OpenBB Terminal Function
---

# gh

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
