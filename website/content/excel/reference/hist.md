<!-- markdownlint-disable MD041 -->

Get historical data by providing symbol and field tag.

## Syntax

```excel wordwrap
=OBB.HIST(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for, e.g. 'AAPL'. | False |
| field | Text | Field to get data for, e.g. 'ebitda'. | False |
| start_date | Text | Start date of the data, in YYYY-MM-DD format, defaults to 5 years ago. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format, defaults to today. | True |
| frequency | Text | The frequency of the data, can be 'yearly' or 'quarterly', defaults to 'yearly'. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | The value of the data.  |
