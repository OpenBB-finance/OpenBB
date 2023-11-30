<!-- markdownlint-disable MD041 -->

Nominal GDP Data.

```excel wordwrap
=OBB.ECONOMY.GDP.NOMINAL(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: oecd | true |
| units | string | The unit of measurement for the data. Units to get nominal GDP in. Either usd or usd_cap indicating per capita. | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| country | string | Country to get GDP for. (provider: oecd) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | Nominal GDP value on the date.  |
