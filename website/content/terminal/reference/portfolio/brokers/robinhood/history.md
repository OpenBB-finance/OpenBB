---
title: history
description: Learn about the usage and parameters for accessing historical portfolio
  information with spans ranging from a day to all accessible history and intervals
  from 5 minutes to a week.
keywords:
- historical portfolio info
- portfolio history
- historical data
- interval data
- span of data
- usage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio/robinhood/history /brokers - Reference | OpenBB Terminal Docs" />

Historical Portfolio Info

### Usage

```python
history [-s {day,week,month,3month,year,5year,all}] [-i {5minute,10minute,hour,day,week}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| span | Span of historical data | 3month | True | day, week, month, 3month, year, 5year, all |
| interval | Interval to look at portfolio | day | True | 5minute, 10minute, hour, day, week |

---
