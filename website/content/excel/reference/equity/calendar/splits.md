---
title: SPLITS
---

<!-- markdownlint-disable MD041 -->

Calendar Splits. Show Stock Split Calendar.

## Syntax

```excel wordwrap
=OBB.EQUITY.CALENDAR.SPLITS([start_date];[end_date];[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.CALENDAR.SPLITS()
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| provider | Text | Options: fmp, defaults to fmp. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| label | Label of the stock splits.  |
| symbol | Symbol representing the entity requested in the data.  |
| numerator | Numerator of the stock splits.  |
| denominator | Denominator of the stock splits.  |
