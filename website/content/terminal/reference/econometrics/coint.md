---
title: coint
description: OpenBB Terminal Function
---

# coint

Show co-integration between two timeseries

### Usage

```python
usage: coint -t TS [-p] [-s SIGNIFICANT]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ts | The time series you wish to test co-integration on. E.g. historical.open,historical2.close. | None | False | None |
| plot | Plot Z-Values | False | True | None |
| significant | Show only companies that have p-values lower than this percentage | 0 | True | None |
---

