<!-- markdownlint-disable MD012 MD031 MD033 -->

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Search Intrinio data tags.

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.SEARCH_ATTRIBUTES(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| query | string | Query to search for. | false |
| provider | string | Options: intrinio | true |
| limit | number | The number of data entries to return. | true |

## Data

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
