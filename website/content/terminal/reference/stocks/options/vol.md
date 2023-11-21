---
title: vol
description: The 'vol' page provides command-line instructions for plotting volumes.
  It deals with parameters like minimal and maximal strikes, calls, and puts. The
  page is mainly focused on contracts traded today and the plotting of call or put
  options only.
keywords:
- vol
- volume
- contracts traded
- plot volume
- min strike
- max strike
- calls
- puts
- options
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /options/vol - Reference | OpenBB Terminal Docs" />

Plot volume. Volume refers to the number of contracts traded today.

### Usage

```python wordwrap
vol [-m MIN] [-M MAX] [-c] [-p] [-e {2023-11-24,2023-12-01,2023-12-08,2023-12-15,2023-12-22,2023-12-29,2024-01-19,2024-02-16,2024-03-15,2024-04-19,2024-06-21,2024-07-19,2024-09-20,2024-12-20,2025-01-17,2025-06-20,2025-09-19,2025-12-19,2026-01-16,}]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| min | -m  --min | Min strike to plot | -1 | True | None |
| max | -M  --max | Max strike to plot | -1 | True | None |
| calls | -c  --calls | Flag to plot call options only | False | True | None |
| puts | -p  --puts | Flag to plot put options only | False | True | None |
| exp | -e  --expiration | Select expiration date (YYYY-MM-DD) |  | True | 2023-11-24, 2023-12-01, 2023-12-08, 2023-12-15, 2023-12-22, 2023-12-29, 2024-01-19, 2024-02-16, 2024-03-15, 2024-04-19, 2024-06-21, 2024-07-19, 2024-09-20, 2024-12-20, 2025-01-17, 2025-06-20, 2025-09-19, 2025-12-19, 2026-01-16,  |

![vol](https://user-images.githubusercontent.com/46355364/154291303-c23edf53-4242-4d9b-a45e-22ce8a633aa8.png)

---
