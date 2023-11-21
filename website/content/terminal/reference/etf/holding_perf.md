---
title: holding_perf
description: Look at ETF company holdings' performance
keywords:
- etf
- holding_perf
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="etf /holding_perf - Reference | OpenBB Terminal Docs" />

Look at ETF company holdings' performance

### Usage

```python wordwrap
holding_perf [-s START] [-e END] [-l LIMIT]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| start | -s  --start-date | The starting date (format YYYY-MM-DD) to get each holding's price | 2022-11-20 | True | None |
| end | -e  --end-date | The ending date (format YYYY-MM-DD) to get each holding's price | 2023-11-21 | True | None |
| limit | -l  --limit | Number of holdings to get | 20 | True | None |

---
