---
title: pos
description: OpenBB Terminal Function
---

# pos

Get dark pool short positions. [Source: Stockgrid]

### Usage

```python
usage: pos [-l LIMIT] [-s {sv,sv_pct,nsv,nsv_dollar,dpp,dpp_dollar}] [-r]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Limit of tickers to display. | 10 | True | None |
| sort_field | Field for which to sort by, where 'sv': Short Vol. [1M], 'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M], 'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M], 'dpp_dollar': DP Position ($1B) | dpp_dollar | True | sv, sv_pct, nsv, nsv_dollar, dpp, dpp_dollar |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
---

