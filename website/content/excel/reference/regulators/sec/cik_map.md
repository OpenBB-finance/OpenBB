<!-- markdownlint-disable MD041 -->

Get the CIK number corresponding to a ticker symbol.

```excel wordwrap
=OBB.REGULATORS.SEC.CIK_MAP(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. | false |
| provider | string | Options: sec | true |

## Data

| Name | Description |
| ---- | ----------- |
| cik | Central Index Key (provider: sec) |
