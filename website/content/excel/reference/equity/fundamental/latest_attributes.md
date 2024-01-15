<!-- markdownlint-disable MD041 -->

Fetch the latest value of a data tag from Intrinio.

## Syntax

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES(symbol;tag;[provider])
```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES("AAPL";"ebitda")
```

---

## Parameters

| Name | Type | Description | Required |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **True** |
| **tag** | **Text** | **Intrinio data tag ID or code.** | **True** |
| provider | Text | Options: intrinio, defaults to intrinio. | False |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| value | The value of the data.  |
