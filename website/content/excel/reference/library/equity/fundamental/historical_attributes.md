<!-- markdownlint-disable MD041 -->

Fetch the historical values of a data tag from Intrinio.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_ATTRIBUTES(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| tag | Text | Intrinio data tag ID or code. | False |
| provider | Text | Options: intrinio | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | True |
| frequency | Text | The frequency of the data. | True |
| limit | Number | The number of data entries to return. | True |
| type | Text | Filter by type, when applicable. | True |
| sort | Text | Sort order. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | The value of the data.  |
