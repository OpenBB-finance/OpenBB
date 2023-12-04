---
title: dpcredit
description: Discount Window Primary Credit Rate
keywords: 
- fixedincome
- rate
- dpcredit
---

<!-- markdownlint-disable MD041 -->

Discount Window Primary Credit Rate.  A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.DPCREDIT(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| parameter | Text | FRED series ID of DWPCR data. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | Discount Window Primary Credit Rate.  |
