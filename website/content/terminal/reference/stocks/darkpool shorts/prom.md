---
title: prom
description: OpenBB Terminal Function
---

# prom

Display dark pool (ATS) data of tickers with growing trades activity using linear regression.

### Usage

```python
usage: prom [-n N_NUM] [-l LIMIT] [-t {T1,T2,OTCE}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| n_num | Number of tickers to filter from entire ATS data based on the sum of the total weekly shares quantity. | 1000 | True | None |
| limit | Limit of most promising tickers to display. | 10 | True | None |
| tier | Tier to process data from. |  | True | T1, T2, OTCE |
---

