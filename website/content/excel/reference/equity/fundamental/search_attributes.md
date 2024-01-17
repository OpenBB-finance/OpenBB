---
title: SEARCH_ATTRIBUTES
---

<!-- markdownlint-disable MD033 -->
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="EQUITY.FUNDAMENTAL.SEARCH_ATTRIBUTES | OpenBB Add-in for Excel Docs" />

Search Intrinio data tags.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.SEARCH_ATTRIBUTES(query;[limit];[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.SEARCH_ATTRIBUTES("ebitda")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **query** | **Text** | **Query to search for.** | **True** |
| limit | Number | The number of data entries to return. | False |
| provider | Text | Options: intrinio, defaults to intrinio. | False |

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
