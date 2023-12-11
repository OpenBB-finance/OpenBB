<!-- markdownlint-disable MD041 -->

Search Intrinio data tags.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.SEARCH_ATTRIBUTES(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| query | Text | Query to search for. | False |
| provider | Text | Options: intrinio | True |
| limit | Number | The number of data entries to return. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| id | ID of the financial attribute.  |
| name | Name of the financial attribute.  |
| tag | Tag of the financial attribute.  |
| statement_code | Code of the financial statement.  |
| statement_type | Type of the financial statement.  |
| parent_name | Parent's name of the financial attribute.  |
| sequence | Sequence of the financial statement.  |
| factor | Unit of the financial attribute.  |
| transaction | Transaction type (credit/debit) of the financial attribute.  |
| type | Type of the financial attribute.  |
| unit | Unit of the financial attribute.  |
