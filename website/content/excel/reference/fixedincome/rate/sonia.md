---
title: SONIA
description: Sterling Overnight Index Average
keywords: 
- fixedincome
- rate
- sonia
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="FIXEDINCOME.RATE.SONIA | OpenBB Add-in for Excel Docs" />

Sterling Overnight Index Average.  SONIA (Sterling Overnight Index Average) is an important interest rate benchmark. SONIA is based on actual transactions and reflects the average of the interest rates that banks pay to borrow sterling overnight from other financial institutions and other institutional investors.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.SONIA([start_date];[end_date];[provider];[parameter])
```

### Example

```excel wordwrap
=OBB.FIXEDINCOME.RATE.SONIA()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fred, defaults to fred. | False |
| parameter | Text | Period of SONIA rate. (provider: fred) | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| rate | SONIA rate.  |
