---
title: arkord
description: OpenBB Terminal Function
---

# arkord

Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]

### Usage

```python
usage: arkord [-l LIMIT] [-s {date,volume,open,high,close,low,total,weight,shares}] [-r] [-b] [-c] [--fund {ARKK,ARKF,ARKW,ARKQ,ARKG,ARKX,}]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of stocks to display. | 10 | True | None |
| sort_col | Column to sort by |  | True | date, volume, open, high, close, low, total, weight, shares |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| buys_only | Flag to look at buys only | False | True | None |
| sells_only | Flag to look at sells only | False | True | None |
| fund | Filter by fund |  | True | ARKK, ARKF, ARKW, ARKQ, ARKG, ARKX,  |
---

