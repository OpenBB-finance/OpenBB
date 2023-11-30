<!-- markdownlint-disable MD041 -->

Equity Ownership. Information about the company ownership.

```excel wordwrap
=OBB.EQUITY.OWNERSHIP.MAJOR_HOLDERS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: fmp | true |
| date | string | A specific date to get data for. | true |
| page | number | Page number of the data to fetch. | true |

## Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| filing_date | Filing date of the stock ownership.  |
| investor_name | Investor name of the stock ownership.  |
| symbol | Symbol representing the entity requested in the data.  |
| security_name | Security name of the stock ownership.  |
| type_of_security | Type of security of the stock ownership.  |
| security_cusip | Security cusip of the stock ownership.  |
| shares_type | Shares type of the stock ownership.  |
| put_call_share | Put call share of the stock ownership.  |
| investment_discretion | Investment discretion of the stock ownership.  |
| industry_title | Industry title of the stock ownership.  |
| weight | Weight of the stock ownership.  |
| last_weight | Last weight of the stock ownership.  |
| change_in_weight | Change in weight of the stock ownership.  |
| change_in_weight_percentage | Change in weight percentage of the stock ownership.  |
| market_value | Market value of the stock ownership.  |
| last_market_value | Last market value of the stock ownership.  |
| change_in_market_value | Change in market value of the stock ownership.  |
| change_in_market_value_percentage | Change in market value percentage of the stock ownership.  |
| shares_number | Shares number of the stock ownership.  |
| last_shares_number | Last shares number of the stock ownership.  |
| change_in_shares_number | Change in shares number of the stock ownership.  |
| change_in_shares_number_percentage | Change in shares number percentage of the stock ownership.  |
| quarter_end_price | Quarter end price of the stock ownership.  |
| avg_price_paid | Average price paid of the stock ownership.  |
| is_new | Is the stock ownership new.  |
| is_sold_out | Is the stock ownership sold out.  |
| ownership | How much is the ownership.  |
| last_ownership | Last ownership amount.  |
| change_in_ownership | Change in ownership amount.  |
| change_in_ownership_percentage | Change in ownership percentage.  |
| holding_period | Holding period of the stock ownership.  |
| first_added | First added date of the stock ownership.  |
| performance | Performance of the stock ownership.  |
| performance_percentage | Performance percentage of the stock ownership.  |
| last_performance | Last performance of the stock ownership.  |
| change_in_performance | Change in performance of the stock ownership.  |
| is_counted_for_performance | Is the stock ownership counted for performance.  |
