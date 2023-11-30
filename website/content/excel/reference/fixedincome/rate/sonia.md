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

```excel wordwrap
=OBB.FIXEDINCOME.RATE.SONIA(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fred | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| parameter | string | Period of SONIA rate. (provider: fred) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SONIA rate.  |
