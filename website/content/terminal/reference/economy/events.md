---
title: events
description: OpenBB Terminal Function
---

# events

Economic calendar. If no start or end dates, default is the current day high importance events.

### Usage

```python
usage: events [-c COUNTRY] [-s START_DATE] [-e END_DATE] [-d SPEC_DATE] [-i {high,medium,low,all}] [--categories {employment,credit,balance,economic_activity,central_banks,bonds,inflation,confidence_index}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| country | Display calendar for specific country. |  | True | None |
| start_date | The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) | 2022-11-22 | True | None |
| end_date | The start date of the data (format: YEAR-MONTH-DAY, i.e. 2010-12-31) | 2022-11-22 | True | None |
| spec_date | Get a specific date for events. Overrides start and end dates. | None | True | None |
| importance | Event importance classified as high, medium, low or all. | None | True | high, medium, low, all |
| category | [INVESTING source only] Event category. | None | True | employment, credit, balance, economic_activity, central_banks, bonds, inflation, confidence_index |
---

