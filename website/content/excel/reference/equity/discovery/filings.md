<!-- markdownlint-disable MD041 -->

Get the most-recent filings submitted to the SEC.

```excel wordwrap
=OBB.EQUITY.DISCOVERY.FILINGS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| form_type | string | Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types. | true |
| limit | number | The number of data entries to return. | true |
| isDone | boolean | Flag for whether or not the filing is done. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| title | Title of the filing.  |
| date | The date of the data.  |
| form_type | The form type of the filing  |
| link | URL to the filing page on the SEC site.  |
