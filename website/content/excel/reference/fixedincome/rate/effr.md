---
title: EFFR
description: Fed Funds Rate
keywords: 
- fixedincome
- rate
- effr
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.RATE.EFFR | OpenBB Add-in for Excel Docs" />

Fed Funds Rate.  Get Effective Federal Funds Rate data. A bank rate is the interest rate a nation's central bank charges to its domestic banks to borrow money. The rates central banks charge are set to stabilize the economy. In the United States, the Federal Reserve System's Board of Governors set the bank rate, also known as the discount rate.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.EFFR([start_date];[end_date];[provider];[parameter])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.RATE.EFFR()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: federal_reserve, fred, defaults to federal_reserve. | False |
| parameter | Text | Period of FED rate. (provider: fred) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | FED rate.  |
