---
title: revenue_per_segment
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

<!-- markdownlint-disable MD041 -->

Revenue Business Line. Business line revenue data.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_SEGMENT(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp | True |
| period | Text | Time period of the data to return. | True |
| structure | Text | Structure of the returned data. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| business_line | Day level data containing the revenue of the business line.  |
