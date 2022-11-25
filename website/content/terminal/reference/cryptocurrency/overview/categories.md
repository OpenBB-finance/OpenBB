---
title: categories
description: OpenBB Terminal Function
---

# categories

Shows top cryptocurrency categories by market capitalization. It includes categories like: stablecoins, defi, solana ecosystem, polkadot ecosystem and many others. You can sort by {}, using --sortby parameter

### Usage

```python
usage: categories [-l LIMIT] [-s {Name,Market_Cap,Market_Cap_Change_24H,Top_3_Coins,Volume_24H}] [--pie]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| limit | display N number of records | 15 | True | None |
| sortby | Sort by given column. Default: market_cap_desc | Market_Cap | True | Name, Market_Cap, Market_Cap_Change_24H, Top_3_Coins, Volume_24H |
| pie | Flag to show pie chart | False | True | None |
---

