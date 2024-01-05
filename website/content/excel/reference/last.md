<!-- markdownlint-disable MD041 -->

Get latest data point by providing stock symbol and tag. See tag options at: https://data.intrinio.com/data-tags.

## Syntax

```excel wordwrap
=OBB.LAST(symbol;tag)
```

---

## Example

```excel wordwrap
=OBB.LAST("AAPL";"EBITDA")
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| **symbol** | **Text** | **Symbol to get data for, e.g. 'AAPL'.** | **False** |
| **tag** | **Text** | **Field tag to get data for, e.g. 'EBITDA'. See options at: https://data.intrinio.com/data-tags.** | **False** |

---

## Return Data

| Name | Description |
| ---- | ----------- |
| value | The value of the data.  |
