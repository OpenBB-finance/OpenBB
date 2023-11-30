---
title: ameribor
description: Ameribor
keywords: 
- fixedincome
- rate
- ameribor
---

<!-- markdownlint-disable MD041 -->

Ameribor.  Ameribor (short for the American interbank offered rate) is a benchmark interest rate that reflects the true cost of short-term interbank borrowing. This rate is based on transactions in overnight unsecured loans conducted on the American Financial Exchange (AFX).

```excel wordwrap
=OBB.FIXEDINCOME.RATE.AMERIBOR(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| parameter | string | Period of AMERIBOR rate. (provider: fred) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | AMERIBOR rate.  |
