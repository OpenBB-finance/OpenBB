<!-- markdownlint-disable MD041 -->

Fetch the latest value of a data tag from Intrinio.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES(required;[optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | Text | Symbol to get data for. | False |
| tag | Text | Intrinio data tag ID or code. | False |
| provider | Text | Options: intrinio | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| value | The value of the data.  |
