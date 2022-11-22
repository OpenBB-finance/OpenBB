---
title: ldapps
description: OpenBB Terminal Function
---

# ldapps

Display information about listed dApps on DeFi Llama. [Source: https://docs.llama.fi/api]

### Usage

```python
usage: ldapps [-l LIMIT] [-s {tvl,symbol,category,chains,change_1h,change_1d,change_7d,name}] [-r] [--desc]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | Number of records to display | 10 | True | None |
| sortby | Sort by given column. Default: tvl | tvl | True | tvl, symbol, category, chains, change_1h, change_1d, change_7d, name |
| reverse | Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. | False | True | None |
| description | Flag to display description of protocol | False | True | None |
---

