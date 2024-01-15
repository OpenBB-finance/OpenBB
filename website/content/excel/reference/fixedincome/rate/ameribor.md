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

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.AMERIBOR([start_date];[end_date];[provider];[parameter])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.RATE.AMERIBOR()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fred, defaults to fred. | False |
| parameter | Text | Period of AMERIBOR rate. (provider: fred) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | AMERIBOR rate.  |
