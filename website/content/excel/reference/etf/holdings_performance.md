<!-- markdownlint-disable MD041 -->

Get the ETF holdings performance.

```excel wordwrap
=OBB.ETF.HOLDINGS_PERFORMANCE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| one_day | One-day return.  |
| wtd | Week to date return.  |
| one_week | One-week return.  |
| mtd | Month to date return.  |
| one_month | One-month return.  |
| qtd | Quarter to date return.  |
| three_month | Three-month return.  |
| six_month | Six-month return.  |
| ytd | Year to date return.  |
| one_year | One-year return.  |
| three_year | Three-year return.  |
| five_year | Five-year return.  |
| ten_year | Ten-year return.  |
| max | Return from the beginning of the time series.  |
| symbol | The ticker symbol. (provider: fmp) |
