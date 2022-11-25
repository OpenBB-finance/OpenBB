---
title: granger
description: OpenBB Terminal Function
---

# granger

Show Granger causality between two timeseries

### Usage

```python
usage: granger [-t Available time series] [-l LAGS] [-c CONFIDENCE]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| ts | Requires two time series, the first time series is assumed to be Granger-caused by the second time series. | None | True | None |
| lags | How many lags should be included | 3 | True | None |
| confidence | Set the confidence level | 0.05 | True | None |
---

