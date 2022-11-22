---
title: unu
description: OpenBB Terminal Function
---

# unu

This command gets unusual options from fdscanner.com

### Usage

```python
usage: unu [-l LIMIT] [-s {Strike,Vol/OI,Vol,OI,Bid,Ask,Exp,Ticker} [{Strike,Vol/OI,Vol,OI,Bid,Ask,Exp,Ticker} ...]] [-r] [-p] [-c]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of options to show. Each scraped page gives 20 results. | 20 | True | None |
| sortby | Column to sort by. Vol/OI is the default and typical variable to be considered unusual. | Vol/OI | True | Strike, Vol/OI, Vol, OI, Bid, Ask, Exp, Ticker |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| puts_only | Flag to show puts only | False | True | None |
| calls_only | Flag to show calls only | False | True | None |
---

