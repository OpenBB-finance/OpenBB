---
title: moody
description: Moody's Aaa and Baa are investment bonds that acts as an index of the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectivelyThese corporate bonds often are used in macroeconomics as an alternative to the federal ten-year Treasury Bill as an indicator of the interest rate
keywords:
- fixedincome
- moody
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="fixedincome /moody - Reference | OpenBB Terminal Docs" />

Moody's Aaa and Baa are investment bonds that acts as an index of the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectivelyThese corporate bonds often are used in macroeconomics as an alternative to the federal ten-year Treasury Bill as an indicator of the interest rate.

### Usage

```python wordwrap
moody [-t {aaa,baa}] [--spread {treasury,fed_funds}] [-s START_DATE] [-e END_DATE]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| data_type | -t  --type | What type you'd like to collect data for | aaa | True | aaa, baa |
| spread | --spread | Whether you want to show the spread | None | True | treasury, fed_funds |
| start_date | -s  --start | Starting date (YYYY-MM-DD) of data | 1980-01-01 | True | None |
| end_date | -e  --end | Ending date (YYYY-MM-DD) of data | None | True | None |

---
