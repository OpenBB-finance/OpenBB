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

```jsx<span style={color: 'red'}>=OBB.FIXEDINCOME.RATE.AMERIBOR([provider];[start_date];[end_date];[parameter])</span>```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.RATE.AMERIBOR()
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred, defaults to fred. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| parameter | Text | Period of AMERIBOR rate. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | AMERIBOR rate.  |
