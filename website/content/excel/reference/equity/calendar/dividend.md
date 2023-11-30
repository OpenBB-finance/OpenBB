<!-- markdownlint-disable MD041 -->

Upcoming and Historical Dividend Calendar.

```excel wordwrap
=OBB.EQUITY.CALENDAR.DIVIDEND(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp, intrinio | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| symbol | string | Symbol to get data for. (provider: intrinio) | true |
| page_size | number | The number of data entries to return. (provider: intrinio) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data. (Ex-Dividend)  |
| symbol | Symbol representing the entity requested in the data.  |
| amount | Dividend amount, per-share.  |
| name | Name of the entity.  |
| record_date | The record date of ownership for eligibility.  |
| payment_date | The payment date of the dividend.  |
| declaration_date | Declaration date of the dividend.  |
| adjusted_amount | The adjusted-dividend amount. (provider: fmp) |
| label | Ex-dividend date formatted for display. (provider: fmp) |
