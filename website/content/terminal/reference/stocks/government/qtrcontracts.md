---
title: qtrcontracts
description: OpenBB Terminal Function
---

# qtrcontracts

Look at government contracts [Source: www.quiverquant.com]

### Usage

```python
usage: qtrcontracts [-l LIMIT] [-a {total,upmom,downmom}] [--raw]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of tickers to get | 5 | True | None |
| analysis | Analysis to look at contracts. 'Total' shows summed contracts. 'Upmom' shows highest sloped contacts while 'downmom' shows highest decreasing slopes. | total | True | total, upmom, downmom |
| raw | Print raw data. | False | True | None |
---

