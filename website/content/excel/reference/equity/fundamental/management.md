<!-- markdownlint-disable MD041 -->

Key Executives. Key executives for a given company.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.MANAGEMENT(required, [optional])
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
| title | Designation of the key executive.  |
| name | Name of the key executive.  |
| pay | Pay of the key executive.  |
| currency_pay | Currency of the pay.  |
| gender | Gender of the key executive.  |
| year_born | Birth year of the key executive.  |
| title_since | Date the tile was held since.  |
