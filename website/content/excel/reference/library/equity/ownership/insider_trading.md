---
title: insider_trading
description: Learn how to use the stock insider trading Python function to get information
  about insider trading, including parameter details, return types, and data descriptions.
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

<!-- markdownlint-disable MD041 -->

Insider Trading. Information about insider trading.

## Syntax

```excel wordwrap
=OBB.EQUITY.OWNERSHIP.INSIDER_TRADING(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| provider | Text | Options: fmp, intrinio | True |
| limit | Number | The number of data entries to return. | True |
| transactionType | Any | Type of the transaction. (provider: fmp) | True |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. (provider: intrinio) | True |
| end_date | Text | End date of the data, in YYYY-MM-DD format. (provider: intrinio) | True |
| ownership_type | Text | Type of ownership. (provider: intrinio) | True |
| sort_by | Text | Field to sort by. (provider: intrinio) | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| symbol | Symbol representing the entity requested in the data.  |
| company_cik | Company CIK of the insider trading.  |
| filing_date | Filing date of the insider trading.  |
| transaction_date | Transaction date of the insider trading.  |
| owner_cik | Reporting CIK of the insider trading.  |
| owner_name | Reporting name of the insider trading.  |
| owner_title | Designation of owner of the insider trading.  |
| transaction_type | Transaction type of the insider trading.  |
| acquisition_or_disposition | Acquisition or disposition of the insider trading.  |
| security_type | Security type of the insider trading.  |
| securities_owned | Number of securities owned in the insider trading.  |
| securities_transacted | Securities transacted of the insider trading.  |
| transaction_price | Price of the insider trading.  |
| filing_url | Link of the insider trading.  |
| form_type | Form type of the insider trading. (provider: fmp) |
| company_name | Name of the company. (provider: intrinio) |
| conversion_exercise_price | Conversion/Exercise price of the insider trading. (provider: intrinio) |
| deemed_execution_date | Deemed execution date of the insider trading. (provider: intrinio) |
| exercise_date | Exercise date of the insider trading. (provider: intrinio) |
| expiration_date | Expiration date of the insider trading. (provider: intrinio) |
| underlying_security_title | Name of the underlying non-derivative security related to this derivative transaction. (provider: intrinio) |
| underlying_shares | Number of underlying shares related to this derivative transaction. (provider: intrinio) |
| nature_of_ownership | Nature of ownership of the insider trading. (provider: intrinio) |
| director | Whether the owner is a director. (provider: intrinio) |
| officer | Whether the owner is an officer. (provider: intrinio) |
| ten_percent_owner | Whether the owner is a 10% owner. (provider: intrinio) |
| other_relation | Whether the owner is having another relation. (provider: intrinio) |
| derivative_transaction | Whether the owner is having a derivative transaction. (provider: intrinio) |
| report_line_number | Report line number of the insider trading. (provider: intrinio) |
