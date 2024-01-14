<!-- markdownlint-disable MD041 -->

Fetch the latest value of a data tag from Intrinio.

## Syntax

```jsx<span style={color: 'red'}>=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES(symbol;tag;[provider])</span>```

### Example

```excel wordwrap
=OBB.EQUITY.FUNDAMENTAL.LATEST_ATTRIBUTES("AAPL";"EBITDA")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for.** | **False** |
| **tag** | **Text** | **Intrinio data tag ID or code.** | **False** |
| provider | Text | Options: intrinio, defaults to intrinio. | True |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| value | The value of the data.  |
