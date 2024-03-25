---
title: "insider_trading"
description: "Learn how to use the stock insider trading Python function to get information  about insider trading, including parameter details, return types, and data descriptions."
keywords:
- stock insider trading
- equity ownership
- Python function
- parameter details
- data description
- symbol
- transaction type
- limit
- provider
- returns
- results
- chart
- metadata
- data
- filing date
- transaction date
- reporting CIK
- securities owned
- company CIK
- reporting name
- type of owner
- acquisition or disposition
- form type
- securities transacted
- price
- security name
- link
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="equity/ownership/insider_trading - Reference | OpenBB Platform Docs" />

<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Get data about trading by a company's management team and board of directors.


Examples
--------

```python
from openbb import obb
obb.equity.ownership.insider_trading(symbol='AAPL', provider='fmp')
obb.equity.ownership.insider_trading(symbol='AAPL', limit=500, provider='intrinio')
```

---

## Parameters

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 500 | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 500 | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| transaction_type | Literal[None, 'award', 'conversion', 'return', 'expire_short', 'in_kind', 'gift', 'expire_long', 'discretionary', 'other', 'small', 'exempt', 'otm', 'purchase', 'sale', 'tender', 'will', 'itm', 'trust'] | Type of the transaction. | None | True |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 500 | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| start_date | Union[date, str] | Start date of the data, in YYYY-MM-DD format. |  | False |
| end_date | Union[date, str] | End date of the data, in YYYY-MM-DD format. |  | False |
| ownership_type | Literal['D', 'I'] | Type of ownership. | None | True |
| sort_by | Literal['filing_date', 'updated_on'] | Field to sort by. | updated_on | True |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for. |  | False |
| limit | int | The number of data entries to return. | 500 | True |
| provider | Literal['fmp', 'intrinio', 'tmx'] | The provider to use for the query, by default None. If None, the provider specified in defaults is selected or 'fmp' if there is no default. | fmp | True |
| summary | bool | Return a summary of the insider activity instead of the individuals. | False | True |
</TabItem>

</Tabs>

---

## Returns

```python wordwrap
OBBject
    results : InsiderTrading
        Serializable results.
    provider : Literal['fmp', 'intrinio', 'tmx']
        Provider name.
    warnings : Optional[List[Warning_]]
        List of warnings.
    chart : Optional[Chart]
        Chart object.
    extra : Dict[str, Any]
        Extra info.

```

---

## Data

<Tabs>

<TabItem value='standard' label='standard'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| company_cik | Union[int, str] | CIK number of the company. |
| filing_date | Union[date, datetime] | Filing date of the trade. |
| transaction_date | date | Date of the transaction. |
| owner_cik | Union[int, str] | Reporting individual's CIK. |
| owner_name | str | Name of the reporting individual. |
| owner_title | str | The title held by the reporting individual. |
| transaction_type | str | Type of transaction being reported. |
| acquisition_or_disposition | str | Acquisition or disposition of the shares. |
| security_type | str | The type of security transacted. |
| securities_owned | float | Number of securities owned by the reporting individual. |
| securities_transacted | float | Number of securities transacted by the reporting individual. |
| transaction_price | float | The price of the transaction. |
| filing_url | str | Link to the filing. |
</TabItem>

<TabItem value='fmp' label='fmp'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| company_cik | Union[int, str] | CIK number of the company. |
| filing_date | Union[date, datetime] | Filing date of the trade. |
| transaction_date | date | Date of the transaction. |
| owner_cik | Union[int, str] | Reporting individual's CIK. |
| owner_name | str | Name of the reporting individual. |
| owner_title | str | The title held by the reporting individual. |
| transaction_type | str | Type of transaction being reported. |
| acquisition_or_disposition | str | Acquisition or disposition of the shares. |
| security_type | str | The type of security transacted. |
| securities_owned | float | Number of securities owned by the reporting individual. |
| securities_transacted | float | Number of securities transacted by the reporting individual. |
| transaction_price | float | The price of the transaction. |
| filing_url | str | Link to the filing. |
| form_type | str | Form type of the insider trading. |
</TabItem>

<TabItem value='intrinio' label='intrinio'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| company_cik | Union[int, str] | CIK number of the company. |
| filing_date | Union[date, datetime] | Filing date of the trade. |
| transaction_date | date | Date of the transaction. |
| owner_cik | Union[int, str] | Reporting individual's CIK. |
| owner_name | str | Name of the reporting individual. |
| owner_title | str | The title held by the reporting individual. |
| transaction_type | str | Type of transaction being reported. |
| acquisition_or_disposition | str | Acquisition or disposition of the shares. |
| security_type | str | The type of security transacted. |
| securities_owned | float | Number of securities owned by the reporting individual. |
| securities_transacted | float | Number of securities transacted by the reporting individual. |
| transaction_price | float | The price of the transaction. |
| filing_url | str | Link to the filing. |
| company_name | str | Name of the company. |
| conversion_exercise_price | float | Conversion/Exercise price of the shares. |
| deemed_execution_date | date | Deemed execution date of the trade. |
| exercise_date | date | Exercise date of the trade. |
| expiration_date | date | Expiration date of the derivative. |
| underlying_security_title | str | Name of the underlying non-derivative security related to this derivative transaction. |
| underlying_shares | Union[int, float] | Number of underlying shares related to this derivative transaction. |
| nature_of_ownership | str | Nature of ownership of the insider trading. |
| director | bool | Whether the owner is a director. |
| officer | bool | Whether the owner is an officer. |
| ten_percent_owner | bool | Whether the owner is a 10% owner. |
| other_relation | bool | Whether the owner is having another relation. |
| derivative_transaction | bool | Whether the owner is having a derivative transaction. |
| report_line_number | int | Report line number of the insider trading. |
</TabItem>

<TabItem value='tmx' label='tmx'>

| Name | Type | Description |
| ---- | ---- | ----------- |
| symbol | str | Symbol representing the entity requested in the data. |
| company_cik | Union[int, str] | CIK number of the company. |
| filing_date | Union[date, datetime] | Filing date of the trade. |
| transaction_date | date | Date of the transaction. |
| owner_cik | Union[int, str] | Reporting individual's CIK. |
| owner_name | str | Name of the reporting individual. |
| owner_title | str | The title held by the reporting individual. |
| transaction_type | str | Type of transaction being reported. |
| acquisition_or_disposition | str | Acquisition or disposition of the shares. |
| security_type | str | The type of security transacted. |
| securities_owned | float | Number of securities owned by the reporting individual. |
| securities_transacted | float | Number of securities transacted by the reporting individual. |
| transaction_price | float | The price of the transaction. |
| filing_url | str | Link to the filing. |
| period | str | The period of the activity. Bucketed by three, six, and twelve months. |
| acquisition_or_deposition | str | Whether the insider bought or sold the shares. |
| number_of_trades | int | The number of shares traded over the period. |
| trade_value | float | The value of the shares traded by the insider. |
| securities_bought | int | The total number of shares bought by all insiders over the period. |
| securities_sold | int | The total number of shares sold by all insiders over the period. |
| net_activity | int | The total net activity by all insiders over the period. |
</TabItem>

</Tabs>

