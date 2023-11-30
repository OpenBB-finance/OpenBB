<!-- markdownlint-disable MD041 -->

Economic Calendar.

```excel wordwrap
=OBB.ECONOMY.CALENDAR(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| provider | string | Options: fmp, tradingeconomics | true |
| start_date | string | Start date of the data, in YYYY-MM-DD format. | true |
| end_date | string | End date of the data, in YYYY-MM-DD format. | true |
| country | any | Country of the event (provider: tradingeconomics) | true |
| importance | string | Importance of the event. (provider: tradingeconomics) | true |
| group | string | Grouping of events (provider: tradingeconomics) | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| country | Country of event.  |
| event | Event name.  |
| reference | Abbreviated period for which released data refers to.  |
| source | Source of the data.  |
| sourceurl | Source URL.  |
| actual | Latest released value.  |
| previous | Value for the previous period after the revision (if revision is applicable).  |
| consensus | Average forecast among a representative group of economists.  |
| forecast | Trading Economics projections  |
| url | Trading Economics URL  |
| importance | Importance of the event. 1-Low, 2-Medium, 3-High  |
| currency | Currency of the data.  |
| unit | Unit of the data.  |
| change | Value change since previous. (provider: fmp) |
| change_percent | Percentage change since previous. (provider: fmp) |
| updated_at | Last updated timestamp. (provider: fmp) |
| created_at | Created at timestamp. (provider: fmp) |
