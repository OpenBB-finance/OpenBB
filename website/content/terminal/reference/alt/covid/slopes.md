---
title: slopes
description: This page offers information on the 'slopes' Python function, which displays
  the countries with the highest slope values. You can customize the data displayed
  with parameters such as 'days back', 'reverse' for sorting options, and 'threshold'
  for total cases.
keywords:
- slope
- data sorting
- data analysis
- cases threshold
- ascending
- descending
- reverse
- days back
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt/covid/slopes - Reference | OpenBB Terminal Docs" />

Show countries with highest slopes.

### Usage

```python
slopes [-d DAYS] [-r] [-t THRESHOLD]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| days | Number of days back to look | 30 | True | None |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| threshold | Threshold for total cases over period | 10000 | True | None |

---
