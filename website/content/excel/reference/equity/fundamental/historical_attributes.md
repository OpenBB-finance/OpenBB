---
title: HISTORICAL_ATTRIBUTES
---

<!-- markdownlint-disable MD041 -->

Fetch the historical values of a data tag from Intrinio.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_ATTRIBUTES(symbol;tag;[start_date];[end_date];[frequency];[limit];[type];[sort];[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.HISTORICAL_ATTRIBUTES("AAPL";"ebitda")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| **tag** | **Text** | **Intrinio data tag ID or code.** | **True** |
| start_date | Text | Start date of the data, in YYYY-MM-DD format. | False |
| end_date | Text | End date of the data, in YYYY-MM-DD format. | False |
| frequency | Text | The frequency of the data. | False |
| limit | Number | The number of data entries to return. | False |
| type | Text | Filter by type, when applicable. | False |
| sort | Text | Sort order. | False |
| provider | Text | Options: intrinio, defaults to intrinio. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| date | The date of the data.  |
| value | The value of the data.  |
