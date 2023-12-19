---
title: ftd
description: Documentation and usage guide for the 'ftd' function that prints the
  latest fails-to-deliver data sourced from SEC. It allows users to specify date range,
  volume of data and offers raw data print.
keywords:
- fails-to-deliver data
- SEC source
- ftd
- datetime parameter
- raw data
- data print
- data analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks/dps/ftd - Reference | OpenBB Terminal Docs" />

Prints latest fails-to-deliver data. [Source: SEC]

### Usage

```python
ftd [-s START] [-e END] [-n N_NUM] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| start | start of datetime to see FTD | 2022-09-26 | True | None |
| end | end of datetime to see FTD | 2022-11-25 | True | None |
| n_num | number of latest fails-to-deliver being printed | 0 | True | None |
| raw | Print raw data. | False | True | None |

![ftd](https://user-images.githubusercontent.com/46355364/154075166-a5a84604-e8ec-46d5-a990-8ca3d928c662.png)

---
