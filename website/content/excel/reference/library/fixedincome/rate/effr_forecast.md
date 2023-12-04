---
title: effr_forecast
description: Fed Funds Rate Projections
keywords: 
- fixedincome
- rate
- effr_forecast
---

<!-- markdownlint-disable MD041 -->

Fed Funds Rate Projections.  The projections for the federal funds rate are the value of the midpoint of the projected appropriate target range for the federal funds rate or the projected appropriate target level for the federal funds rate at the end of the specified calendar year or over the longer run.

## Syntax

```excel wordwrap
=OBB.FIXEDINCOME.RATE.EFFR_FORECAST(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fred | True |
| long_run | Boolean | Flag to show long run projections (provider: fred) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| range_high | High projection of rates.  |
| central_tendency_high | Central tendency of high projection of rates.  |
| median | Median projection of rates.  |
| range_midpoint | Midpoint projection of rates.  |
| central_tendency_midpoint | Central tendency of midpoint projection of rates.  |
| range_low | Low projection of rates.  |
| central_tendency_low | Central tendency of low projection of rates.  |
