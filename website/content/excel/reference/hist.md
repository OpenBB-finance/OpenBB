<!-- markdownlint-disable MD041 -->

Get historical data by providing symbol and field tag.

```excel wordwrap
=OBB.HIST(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for, e.g. 'AAPL'. | false |
| field | string | Field to get data for, e.g. 'ebitda'. | false |
| start_date | string | Start date of the data, in YYYY-MM-DD format, defaults to 5 years ago. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format, defaults to today. | true |
| frequency | string | The frequency of the data, can be 'yearly' or 'quarterly', defaults to 'yearly'. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | The value of the data.  |
