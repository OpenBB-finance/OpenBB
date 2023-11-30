<!-- markdownlint-disable MD041 -->

ETF Sector weighting.

```excel wordwrap
=OBB.ETF.SECTORS(required, [optional])
```

---

## Parameters

| Name | Type | Description | Optional |
| ---- | ---- | ----------- | -------- |
| symbol | string | Symbol to get data for. (ETF) | false |
| provider | string | Options: fmp | true |

## Data

| Name | Description |
| ---- | ----------- |
| sector | Sector of exposure.  |
| weight | Exposure of the ETF to the sector in normalized percentage points.  |
