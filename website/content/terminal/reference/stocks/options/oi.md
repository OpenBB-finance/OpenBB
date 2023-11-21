---
title: oi
description: This page provides a detailed explanation on how to plot open interest
  using various parameters such as min, max, calls, and puts. It also includes usage
  examples.
keywords:
- Open interest
- Tutorial
- Parameters
- Option trading
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks /options/oi - Reference | OpenBB Terminal Docs" />

Plot open interest. Open interest represents the number of contracts that exist.

### Usage

```python wordwrap
oi [-m MIN] [-M MAX] [-c] [-p] [-e {2023-11-24,2023-12-01,2023-12-08,2023-12-15,2023-12-22,2023-12-29,2024-01-19,2024-02-16,2024-03-15,2024-04-19,2024-06-21,2024-07-19,2024-09-20,2024-12-20,2025-01-17,2025-06-20,2025-09-19,2025-12-19,2026-01-16,}]
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


---

## Examples

```python
2022 Feb 16, 09:13 (🦋) /stocks/options/ $ load SPY

2022 Feb 16, 09:14 (🦋) /stocks/options/ $ exp 10
Expiration set to 2022-03-11

2022 Feb 16, 09:14 (🦋) /stocks/options/ $ oi
```
![oi](https://user-images.githubusercontent.com/46355364/154282811-b8b7d36b-2e4e-44c0-8026-b244d97a8608.png)

---
