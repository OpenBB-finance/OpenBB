---
title: futures
description: OpenBB Terminal Function
---

# futures

Futures/Commodities from Wall St. Journal and FinViz.

### Usage

```python
usage: futures [-c {energy,metals,meats,grains,softs}] [-s {ticker,last,change,prevClose}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| commodity | Obtain commodity futures from FinViz |  | True | energy, metals, meats, grains, softs |
| sortby |  | ticker | True | ticker, last, change, prevClose |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

