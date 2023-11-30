<!-- markdownlint-disable MD041 -->

Equity Info. Get general price and performance metrics of a stock.

```excel wordwrap
=OBB.EQUITY.PROFILE(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: intrinio | true |

## Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| name | Common name of the company.  |
| cik | Central Index Key (CIK) for the requested entity.  |
| lei | Legal Entity Identifier assigned to the company.  |
| legal_name | Official legal name of the company.  |
| stock_exchange | Stock exchange where the company is traded.  |
| sic | Standard Industrial Classification code for the company.  |
| short_description | Short description of the company.  |
| long_description | Long description of the company.  |
| ceo | Chief Executive Officer of the company.  |
| company_url | URL of the company's website.  |
| business_address | Address of the company's headquarters.  |
| mailing_address | Mailing address of the company.  |
| business_phone_no | Phone number of the company's headquarters.  |
| hq_address1 | Address of the company's headquarters.  |
| hq_address2 | Address of the company's headquarters.  |
| hq_address_city | City of the company's headquarters.  |
| hq_address_postal_code | Zip code of the company's headquarters.  |
| hq_state | State of the company's headquarters.  |
| hq_country | Country of the company's headquarters.  |
| inc_state | State in which the company is incorporated.  |
| inc_country | Country in which the company is incorporated.  |
| employees | Number of employees working for the company.  |
| entity_legal_form | Legal form of the company.  |
| entity_status | Status of the company.  |
| latest_filing_date | Date of the company's latest filing.  |
| irs_number | IRS number assigned to the company.  |
| sector | Sector in which the company operates.  |
| industry_category | Category of industry in which the company operates.  |
| industry_group | Group of industry in which the company operates.  |
| template | Template used to standardize the company's financial statements.  |
| standardized_active | Whether the company is active or not.  |
| first_fundamental_date | Date of the company's first fundamental.  |
| last_fundamental_date | Date of the company's last fundamental.  |
| first_stock_price_date | Date of the company's first stock price.  |
| last_stock_price_date | Date of the company's last stock price.  |
| id | Intrinio ID for the company. (provider: intrinio) |
| thea_enabled | Whether the company has been enabled for Thea. (provider: intrinio) |
