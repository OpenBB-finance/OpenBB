<!-- markdownlint-disable MD041 -->

Calendar Splits. Show Stock Split Calendar.

## Syntax

```excel wordwrap
=OBB.EQUITY.CALENDAR.SPLITS( [provider]; [start_date]; [end_date] )
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | Text | Options: fmp, defaults to fmp. | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| label | Label of the stock splits.  |
| symbol | Symbol representing the entity requested in the data.  |
| numerator | Numerator of the stock splits.  |
| denominator | Denominator of the stock splits.  |
---

## Example

```excel wordwrap
=OBB.EQUITY.CALENDAR.SPLITS( )
```

