<!-- markdownlint-disable MD041 -->

Price Target. Price target data.

```excel wordwrap
=OBB.EQUITY.ESTIMATES.PRICE_TARGET(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |
| with_grade | boolean | Include upgrades and downgrades in the response. (provider: fmp) | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| published_date | Published date of the price target.  |
| news_url | News URL of the price target.  |
| news_title | News title of the price target.  |
| analyst_name | Analyst name.  |
| analyst_company | Analyst company.  |
| price_target | Price target.  |
| adj_price_target | Adjusted price target.  |
| price_when_posted | Price when posted.  |
| news_publisher | News publisher of the price target.  |
| news_base_url | News base URL of the price target.  |
| new_grade | New grade (provider: fmp) |
| previous_grade | Previous grade (provider: fmp) |
| grading_company | Grading company (provider: fmp) |
