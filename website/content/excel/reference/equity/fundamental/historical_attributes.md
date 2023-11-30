<!-- markdownlint-disable MD041 -->

Fetch the historical values of a data tag from Intrinio.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_ATTRIBUTES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| tag | string | Intrinio data tag ID or code. | false |
| provider | string | Options: intrinio | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| frequency | string | The frequency of the data. | true |
| limit | number | The number of data entries to return. | true |
| type | string | Filter by type, when applicable. | true |
| sort | string | Sort order. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | The value of the data.  |
