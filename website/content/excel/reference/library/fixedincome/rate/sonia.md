---
title: sonia
description: Sterling Overnight Index Average
keywords: 
- fixedincome
- rate
- sonia
---

<!-- markdownlint-disable MD041 -->

Sterling Overnight Index Average.  SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other financial institutions and other institutional investors.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.SONIA(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| parameter | Text | Period of SONIA rate. (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SONIA rate.  |
