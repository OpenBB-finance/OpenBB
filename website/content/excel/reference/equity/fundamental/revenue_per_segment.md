---
title: REVENUE_PER_SEGMENT
description: Learn how to get revenue data for a specific business line using the
  equity fundamental revenue per segment function.
keywords: 
- Revenue Business Line
- business line revenue data
- equity fundamental revenue per segment
- symbol
- period
- structure
- provider
- results
- RevenueBusinessLine
- chart
- metadata
- data
- date
- business line
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="EQUITY.FUNDAMENTAL.REVENUE_PER_SEGMENT | OpenBB Add-in for Excel Docs" />

Revenue Business Line. Business line revenue data.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_SEGMENT(symbol;[period];[structure];[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_SEGMENT("AAPL")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| period | Text | Time period of the data to return. | False |
| structure | Text | Structure of the returned data. | False |
| provider | Text | Options: fmp, defaults to fmp. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| business_line | Day level data containing the revenue of the business line.  |
