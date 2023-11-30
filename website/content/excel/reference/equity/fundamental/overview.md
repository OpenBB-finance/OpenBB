<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Company Overview. General information about a company.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.OVERVIEW(required, [optional])
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
| symbol | Symbol representing the entity requested in the data.  |
| price | Price of the company.  |
| beta | Beta of the company.  |
| vol_avg | Volume average of the company.  |
| mkt_cap | Market capitalization of the company.  |
| last_div | Last dividend of the company.  |
| range | Range of the company.  |
| changes | Changes of the company.  |
| company_name | Company name of the company.  |
| currency | Currency of the company.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| isin | ISIN of the company.  |
| cusip | CUSIP of the company.  |
| exchange | Exchange of the company.  |
| exchange_short_name | Exchange short name of the company.  |
| industry | Industry of the company.  |
| website | Website of the company.  |
| description | Description of the company.  |
| ceo | CEO of the company.  |
| sector | Sector of the company.  |
| country | Country of the company.  |
| full_time_employees | Full time employees of the company.  |
| phone | Phone of the company.  |
| address | Address of the company.  |
| city | City of the company.  |
| state | State of the company.  |
| zip | Zip of the company.  |
| dcf_diff | Discounted cash flow difference of the company.  |
| dcf | Discounted cash flow of the company.  |
| image | Image of the company.  |
| ipo_date | IPO date of the company.  |
| default_image | If the image is the default image.  |
| is_etf | If the company is an ETF.  |
| is_actively_trading | If the company is actively trading.  |
| is_adr | If the company is an ADR.  |
| is_fund | If the company is a fund.  |
