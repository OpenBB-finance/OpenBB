---
title: "Equity Info"
description: "Get general information about a company"
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

---

## Implementation details

### Class names

| Model name | Parameters class | Data class |
| ---------- | ---------------- | ---------- |
| `EquityInfo` | `EquityInfoQueryParams` | `EquityInfoData` |

### Import Statement

```python
from openbb_core.provider.standard_models.equity_info import (
EquityInfoData,
EquityInfoQueryParams,
)
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | Union[str, List[str]] | Symbol to get data for. Multiple items allowed for provider(s): finviz, fmp, intrinio, tmx, yfinance. |  | False |
| provider | Literal['finviz', 'fmp', 'intrinio', 'tmx', 'yfinance'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'finviz' if there is no default. | finviz | True |
</TabItem>

</Tabs>

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
</TabItem>

<TabItem value='finviz' label='finviz'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
| index | str | Included in indices - i.e., Dow, Nasdaq, or S&P. |
| optionable | str | Whether options trade against the ticker. |
| shortable | str | If the asset is shortable. |
| shares_outstanding | str | The number of shares outstanding, as an abbreviated string. |
| shares_float | str | The number of shares in the public float, as an abbreviated string. |
| short_interest | str | The last reported number of shares sold short, as an abbreviated string. |
| institutional_ownership | float | The institutional ownership of the stock, as a normalized percent. |
| market_cap | str | The market capitalization of the stock, as an abbreviated string. |
| dividend_yield | float | The dividend yield of the stock, as a normalized percent. |
| earnings_date | str | The last, or next confirmed, earnings date and announcement time, as a string. The format is Nov 02 AMC - for after market close. |
| beta | float | The beta of the stock relative to the broad market. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
| is_etf | bool | If the symbol is an ETF. |
| is_actively_trading | bool | If the company is actively trading. |
| is_adr | bool | If the stock is an ADR. |
| is_fund | bool | If the company is a fund. |
| image | str | Image of the company. |
| currency | str | Currency in which the stock is traded. |
| market_cap | int | Market capitalization of the company. |
| last_price | float | The last traded price. |
| year_high | float | The one-year high of the price. |
| year_low | float | The one-year low of the price. |
| volume_avg | int | Average daily trading volume. |
| annualized_dividend_amount | float | The annualized dividend payment based on the most recent regular dividend payment. |
| beta | float | Beta of the stock relative to the market. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
| id | str | Intrinio ID for the company. |
| thea_enabled | bool | Whether the company has been enabled for Thea. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
| email | str | The email of the company. |
| issue_type | str | The issuance type of the asset. |
| shares_outstanding | int | The number of listed shares outstanding. |
| shares_escrow | int | The number of shares held in escrow. |
| shares_total | int | The total number of shares outstanding from all classes. |
| dividend_frequency | str | The dividend frequency. |
</TabItem>

<TabItem value='yfinance' label='yfinance'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| name | str | Common name of the company. |
| cik | str | Central Index Key (CIK) for the requested entity. |
| cusip | str | CUSIP identifier for the company. |
| isin | str | International Securities Identification Number. |
| lei | str | Legal Entity Identifier assigned to the company. |
| legal_name | str | Official legal name of the company. |
| stock_exchange | str | Stock exchange where the company is traded. |
| sic | int | Standard Industrial Classification code for the company. |
| short_description | str | Short description of the company. |
| long_description | str | Long description of the company. |
| ceo | str | Chief Executive Officer of the company. |
| company_url | str | URL of the company's website. |
| business_address | str | Address of the company's headquarters. |
| mailing_address | str | Mailing address of the company. |
| business_phone_no | str | Phone number of the company's headquarters. |
| hq_address1 | str | Address of the company's headquarters. |
| hq_address2 | str | Address of the company's headquarters. |
| hq_address_city | str | City of the company's headquarters. |
| hq_address_postal_code | str | Zip code of the company's headquarters. |
| hq_state | str | State of the company's headquarters. |
| hq_country | str | Country of the company's headquarters. |
| inc_state | str | State in which the company is incorporated. |
| inc_country | str | Country in which the company is incorporated. |
| employees | int | Number of employees working for the company. |
| entity_legal_form | str | Legal form of the company. |
| entity_status | str | Status of the company. |
| latest_filing_date | date | Date of the company's latest filing. |
| irs_number | str | IRS number assigned to the company. |
| sector | str | Sector in which the company operates. |
| industry_category | str | Category of industry in which the company operates. |
| industry_group | str | Group of industry in which the company operates. |
| template | str | Template used to standardize the company's financial statements. |
| standardized_active | bool | Whether the company is active or not. |
| first_fundamental_date | date | Date of the company's first fundamental. |
| last_fundamental_date | date | Date of the company's last fundamental. |
| first_stock_price_date | date | Date of the company's first stock price. |
| last_stock_price_date | date | Date of the company's last stock price. |
| exchange_timezone | str | The timezone of the exchange. |
| issue_type | str | The issuance type of the asset. |
| currency | str | The currency in which the asset is traded. |
| market_cap | int | The market capitalization of the asset. |
| shares_outstanding | int | The number of listed shares outstanding. |
| shares_float | int | The number of shares in the public float. |
| shares_implied_outstanding | int | Implied shares outstanding of common equityassuming the conversion of all convertible subsidiary equity into common. |
| shares_short | int | The reported number of shares short. |
| dividend_yield | float | The dividend yield of the asset, as a normalized percent. |
| beta | float | The beta of the asset relative to the broad market. |
</TabItem>

</Tabs>

