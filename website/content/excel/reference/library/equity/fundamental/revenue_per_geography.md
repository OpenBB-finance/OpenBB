---
title: revenue_per_geography
description: Learn about the revenue per geography data with the geographic revenue
  data Python function in this documentation page. Understand the symbol, period,
  structure, and provider parameters. Explore the returns, results, metadata, and
  the data structure including the date, geographic segment, and revenue by region
  (Americas, Europe, Greater China, Japan, Rest of Asia Pacific).
keywords: 
- geographic revenue data
- revenue per geography
- Python function
- documentation page
- symbol parameter
- period parameter
- structure parameter
- provider parameter
- returns
- results
- metadata
- data
- date
- geographic segment
- Americas
- Europe
- Greater China
- Japan
- Rest of Asia Pacific
---

<!-- markdownlint-disable MD041 -->

Revenue Geographic. Geographic revenue data.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.REVENUE_PER_GEOGRAPHY(required;[optional])
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
| geographic_segment | Day level data containing the revenue of the geographic segment.  |
| americas | Revenue from the the American segment.  |
| europe | Revenue from the the European segment.  |
| greater_china | Revenue from the the Greater China segment.  |
| japan | Revenue from the the Japan segment.  |
| rest_of_asia_pacific | Revenue from the the Rest of Asia Pacific segment.  |
