<!-- markdownlint-disable MD041 -->

Get reported Fail-to-deliver (FTD) data.

```excel wordwrap
=OBB.EQUITY.SHORTS.FAILS_TO_DELIVER(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: sec | true |
| limit | number | Limit the number of reports to parse, from most recent. Approximately 24 reports per year, going back to 2009. (provider: sec) | true |
| skip_reports | number | Skip N number of reports from current. A value of 1 will skip the most recent report. (provider: sec) | true |

## Data

| Name | Description |
| ---- | ----------- |
| settlement_date | The settlement date of the fail.  |
| symbol | Symbol representing the entity requested in the data.  |
| cusip | CUSIP of the Security.  |
| quantity | The number of fails on that settlement date.  |
| price | The price at the previous closing price from the settlement date.  |
| description | The description of the Security.  |
