---
title: tbffr
description: Get Selected Treasury Bill Minus Federal Funds Rate
keywords:
- fixedincome
- tbffr
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /tbffr - Reference | OpenBB Terminal Docs" />

Get Selected Treasury Bill Minus Federal Funds Rate.

### Usage

```python wordwrap
tbffr [-p {3_month,6_month}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| parameter | -p  --parameter | Selected Treasury Bill | 3_month | True | 3_month, 6_month |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | None | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
